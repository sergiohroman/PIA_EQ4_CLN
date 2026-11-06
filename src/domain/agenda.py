"""Aggregate Agenda (N-001, N-007)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from .base import AggregateRoot
from .estados import MAQUINA_CITA, CitaEstado
from .events import CitaAgendadaEvent, CitaCambioEstadoEvent, EmergenciaRegistradaEvent
from .exceptions import NoEncontrado, TraslapeDeCitas, ValidacionDominio
from .servicios import servicio_para
from .specifications import CitaEsEmergencia, CitaSinTraslape
from .value_objects import TipoServicio

HORA_APERTURA = time(8, 0)
HORA_CIERRE = time(20, 0)


@dataclass
class Cita:
    id: str
    mascota_id: str
    veterinario_id: str
    tipo: TipoServicio
    inicio: datetime
    fin: datetime
    estado: CitaEstado = CitaEstado.PROGRAMADA
    es_emergencia: bool = False
    requiere_reprogramacion: bool = False
    celular_propietario: str | None = None

    @property
    def activa(self) -> bool:
        return self.estado in (CitaEstado.PROGRAMADA, CitaEstado.EN_ATENCION)

    def se_traslapa_con(self, otra: "Cita") -> bool:
        return self.inicio < otra.fin and otra.inicio < self.fin

    def transicionar(self, accion: str) -> CitaCambioEstadoEvent:
        anterior = self.estado
        self.estado = MAQUINA_CITA.siguiente(anterior, accion)
        return CitaCambioEstadoEvent(self.id, anterior.value, self.estado.value, accion)


class Agenda(AggregateRoot):
    """Citas de un día. Invariante: sin traslape por veterinario, salvo Emergencia."""

    def __init__(self, fecha: date, citas: list[Cita] | None = None):
        super().__init__()
        self.fecha = fecha
        self.citas: list[Cita] = list(citas or [])

    # -- comandos ---------------------------------------------------------
    def agendar_cita(
        self,
        cita_id: str,
        mascota_id: str,
        tipo: TipoServicio,
        veterinario_id: str,
        inicio: datetime,
        celular_propietario: str | None = None,
        es_emergencia: bool = False,
    ) -> Cita:
        if inicio.date() != self.fecha:
            raise ValidacionDominio("La cita no corresponde a la fecha de esta agenda")
        fin = inicio + servicio_para(tipo).duracion()
        if not es_emergencia and not self._dentro_de_horario(inicio, fin):
            raise ValidacionDominio(
                f"Horario fuera de servicio ({HORA_APERTURA:%H:%M}-{HORA_CIERRE:%H:%M})"
            )
        cita = Cita(
            id=cita_id,
            mascota_id=mascota_id,
            veterinario_id=veterinario_id,
            tipo=tipo,
            inicio=inicio,
            fin=fin,
            es_emergencia=es_emergencia,
            celular_propietario=celular_propietario,
        )
        regla = CitaSinTraslape(self.citas) | CitaEsEmergencia()
        if not regla.is_satisfied_by(cita):
            raise TraslapeDeCitas()
        if es_emergencia:
            for otra in self.citas:
                if (
                    otra.activa
                    and not otra.es_emergencia
                    and otra.veterinario_id == veterinario_id
                    and otra.estado == CitaEstado.PROGRAMADA
                    and otra.se_traslapa_con(cita)
                ):
                    otra.requiere_reprogramacion = True
        self.citas.append(cita)
        if es_emergencia:
            self._registrar(EmergenciaRegistradaEvent(cita.id, mascota_id, veterinario_id))
        else:
            self._registrar(
                CitaAgendadaEvent(
                    cita.id, mascota_id, veterinario_id, tipo.value, inicio, celular_propietario
                )
            )
        return cita

    def transicionar_cita(self, cita_id: str, accion: str) -> Cita:
        cita = self.obtener(cita_id)
        self._registrar(cita.transicionar(accion))
        return cita

    # -- consultas --------------------------------------------------------
    def obtener(self, cita_id: str) -> Cita:
        for cita in self.citas:
            if cita.id == cita_id:
                return cita
        raise NoEncontrado(f"Cita {cita_id} no encontrada")

    def espacios_libres(
        self, veterinario_id: str, tipo: TipoServicio, paso: timedelta = timedelta(minutes=15)
    ) -> list[tuple[datetime, datetime]]:
        """US-02: bloques disponibles para el servicio solicitado."""
        duracion = servicio_para(tipo).duracion()
        regla = CitaSinTraslape(self.citas)
        cierre = datetime.combine(self.fecha, HORA_CIERRE)
        actual = datetime.combine(self.fecha, HORA_APERTURA)
        libres = []
        while actual + duracion <= cierre:
            candidata = Cita("candidata", "-", veterinario_id, tipo, actual, actual + duracion)
            if regla.is_satisfied_by(candidata):
                libres.append((actual, actual + duracion))
            actual += paso
        return libres

    def cola_espera(self) -> list[Cita]:
        """US-03: emergencias primero; el resto por hora de inicio."""
        pendientes = [c for c in self.citas if c.estado == CitaEstado.PROGRAMADA]
        return sorted(pendientes, key=lambda c: (not c.es_emergencia, c.inicio))

    def _dentro_de_horario(self, inicio: datetime, fin: datetime) -> bool:
        return (
            inicio >= datetime.combine(self.fecha, HORA_APERTURA)
            and fin <= datetime.combine(self.fecha, HORA_CIERRE)
        )
