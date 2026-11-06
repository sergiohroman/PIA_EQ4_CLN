"""Specifications concretas del negocio (usan duck typing para no acoplar módulos)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Callable, Iterable

from .estados import CitaEstado, NotaEstado
from .specification import Specification
from .value_objects import TipoServicio


class HospitalizacionTieneCupo(Specification):
    """BR-002 / US-12: candidato = Hospitalizacion."""

    def is_satisfied_by(self, hospitalizacion) -> bool:
        return hospitalizacion.ocupadas() < hospitalizacion.capacidad


class CitaSinTraslape(Specification):
    """N-001: candidato = Cita; no debe traslaparse con citas activas del mismo veterinario."""

    def __init__(self, citas_existentes: Iterable):
        self._citas = list(citas_existentes)

    def is_satisfied_by(self, cita) -> bool:
        return not any(
            c.activa and c.veterinario_id == cita.veterinario_id and c.se_traslapa_con(cita)
            for c in self._citas
        )


class CitaEsEmergencia(Specification):
    """N-007: la emergencia se sobrepone con prioridad máxima."""

    def is_satisfied_by(self, cita) -> bool:
        return bool(cita.es_emergencia)


class CelularNoRegistrado(Specification):
    """N-004 / US-04: candidato = Celular."""

    def __init__(self, existe_celular: Callable[[object], bool]):
        self._existe = existe_celular

    def is_satisfied_by(self, celular) -> bool:
        return not self._existe(celular)


class NotaNoFirmada(Specification):
    """N-005 / US-08: candidato = NotaClinica."""

    def is_satisfied_by(self, nota) -> bool:
        return nota.estado == NotaEstado.BORRADOR


class CitaEsVacuna(Specification):
    """N-008 / US-13: candidato = Cita de tipo vacuna."""

    def is_satisfied_by(self, cita) -> bool:
        return cita.tipo == TipoServicio.VACUNA


class CitaVencida(Specification):
    """N-008 / US-13: la hora de la cita ya pasó respecto a `ahora`."""

    def __init__(self, ahora: datetime):
        self._ahora = ahora

    def is_satisfied_by(self, cita) -> bool:
        return cita.inicio < self._ahora


class CitaConEstado(Specification):
    """La cita se encuentra en alguno de los estados indicados (State Machine de Cita)."""

    def __init__(self, *estados: CitaEstado):
        self._estados = frozenset(estados)

    def is_satisfied_by(self, cita) -> bool:
        return cita.estado in self._estados


def vacuna_atrasada(ahora: datetime) -> Specification:
    """US-13: vacuna vencida que no se aplicó (sigue PROGRAMADA o fue CANCELADA)."""
    return (
        CitaEsVacuna()
        & CitaVencida(ahora)
        & CitaConEstado(CitaEstado.PROGRAMADA, CitaEstado.CANCELADA)
    )


# --- Reglas del paquete de pruebas VetCare 24 (modelo propuesto en el ZIP) ---
# candidato = OperacionVeterinaria


class ActorActivo(Specification):
    def is_satisfied_by(self, operacion) -> bool:
        return bool(operacion.actor_activo)


class OperacionConDetalle(Specification):
    def is_satisfied_by(self, operacion) -> bool:
        return len(operacion.lineas) > 0


class OperacionAutorizada(Specification):
    def is_satisfied_by(self, operacion) -> bool:
        return bool(operacion.autorizado)


class ActorPreferente(Specification):
    def is_satisfied_by(self, operacion) -> bool:
        return bool(operacion.actor_preferente)


class PromocionActiva(Specification):
    def is_satisfied_by(self, operacion) -> bool:
        return bool(operacion.promocion_activa)


class TotalMinimo(Specification):
    def __init__(self, minimo: Decimal):
        self._minimo = Decimal(minimo)

    def is_satisfied_by(self, operacion) -> bool:
        return operacion.total >= self._minimo


class RecursosHabilitados(Specification):
    def is_satisfied_by(self, operacion) -> bool:
        return all(linea.habilitado for linea in operacion.lineas)
