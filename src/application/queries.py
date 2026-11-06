"""Lado de lectura de CQRS (Etapa 6): Queries que no modifican estado."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Callable

from src.domain.estados import CitaEstado
from src.domain.exceptions import NoEncontrado, ValidacionDominio
from src.domain.specifications import vacuna_atrasada

from .dtos import EstadoJaulasDto, HistorialMascotaDto, MascotaSalidaDto, NotaSalidaDto
from .services import UowFactory


@dataclass(frozen=True)
class ConsultarHistorialMascotaQuery:
    mascota_id: str


class ConsultarHistorialMascotaHandler:
    """CE-002: abrir el historial completo de la mascota."""

    def __init__(self, uow_factory: UowFactory):
        self._uow_factory = uow_factory

    def handle(self, query: ConsultarHistorialMascotaQuery) -> HistorialMascotaDto:
        with self._uow_factory() as uow:
            expediente = uow.expedientes.get_by_mascota_id(query.mascota_id)
            if expediente is None:
                raise NoEncontrado(f"Mascota {query.mascota_id} no encontrada")
            return HistorialMascotaDto(
                mascota=MascotaSalidaDto.desde(expediente.obtener_mascota(query.mascota_id)),
                propietario=expediente.propietario.nombre,
                celular=expediente.propietario.celular.valor,
                notas=[NotaSalidaDto.desde(n) for n in expediente.historial(query.mascota_id)],
            )


@dataclass(frozen=True)
class ConsultarOcupacionJaulasQuery:
    pass


class ConsultarOcupacionJaulasHandler:
    """US-15."""

    def __init__(self, uow_factory: UowFactory):
        self._uow_factory = uow_factory

    def handle(self, query: ConsultarOcupacionJaulasQuery) -> EstadoJaulasDto:
        with self._uow_factory() as uow:
            return EstadoJaulasDto.desde(uow.hospitalizacion.obtener_actual())


@dataclass(frozen=True)
class ConsultarProductividadQuery:
    desde: date
    hasta: date


class ConsultarProductividadHandler:
    """US-14: atenciones completadas por veterinario y tipo de servicio."""

    def __init__(self, uow_factory: UowFactory):
        self._uow_factory = uow_factory

    def handle(self, query: ConsultarProductividadQuery) -> list[dict]:
        with self._uow_factory() as uow:
            citas = uow.agendas.listar_rango(query.desde, query.hasta)
            nombres = {v.id: v.nombre for v in uow.veterinarios.listar()}
        conteo: dict[str, dict[str, int]] = defaultdict(lambda: {"consulta": 0, "vacuna": 0, "cirugia": 0})
        for cita in citas:
            if cita.estado == CitaEstado.COMPLETADA:
                conteo[cita.veterinario_id][cita.tipo.value] += 1
        return [
            {
                "veterinario_id": vid,
                "veterinario": nombres.get(vid, vid),
                "consultas": c["consulta"],
                "vacunas": c["vacuna"],
                "cirugias": c["cirugia"],
                "total": sum(c.values()),
            }
            for vid, c in sorted(conteo.items())
        ]


@dataclass(frozen=True)
class ConsultarVacunasPendientesQuery:
    desde: date
    hasta: date


class ConsultarVacunasPendientesHandler:
    """US-13 (N-008): mascotas con vacuna atrasada y contacto de su dueño, para campañas de seguimiento."""

    def __init__(self, uow_factory: UowFactory, ahora: Callable[[], datetime] = datetime.now):
        self._uow_factory = uow_factory
        self._ahora = ahora

    def handle(self, query: ConsultarVacunasPendientesQuery) -> list[dict]:
        if query.desde > query.hasta:
            raise ValidacionDominio("El rango de fechas es inválido: 'desde' es posterior a 'hasta'")
        ahora = self._ahora()
        regla = vacuna_atrasada(ahora)
        filas: list[dict] = []
        with self._uow_factory() as uow:
            citas = sorted(uow.agendas.listar_rango(query.desde, query.hasta), key=lambda c: c.inicio)
            for cita in citas:
                if not regla.is_satisfied_by(cita):
                    continue
                expediente = uow.expedientes.get_by_mascota_id(cita.mascota_id)
                if expediente is None:  # mascota fusionada/eliminada: no hay a quién contactar
                    continue
                mascota = expediente.obtener_mascota(cita.mascota_id)
                filas.append(
                    {
                        "cita_id": cita.id,
                        "mascota_id": mascota.id,
                        "mascota": mascota.nombre,
                        "especie": mascota.especie,
                        "propietario": expediente.propietario.nombre,
                        "celular": expediente.propietario.celular.valor,
                        "fecha_cita": cita.inicio,
                        "estado": cita.estado.value,
                        "dias_atraso": (ahora.date() - cita.inicio.date()).days,
                    }
                )
        return filas
