"""Strategy IServicioCita (SOLID-O, N-001).

Agregar un servicio nuevo (p. ej. estética) = agregar una clase y registrarla,
sin tocar la Agenda. Las duraciones son configurables porque el BRD no las fija.
"""
from abc import ABC, abstractmethod
from datetime import timedelta

from .value_objects import TipoServicio


class IServicioCita(ABC):
    tipo: TipoServicio

    @abstractmethod
    def duracion(self) -> timedelta: ...


class ServicioConsulta(IServicioCita):
    tipo = TipoServicio.CONSULTA

    def duracion(self) -> timedelta:
        return timedelta(minutes=30)


class ServicioVacuna(IServicioCita):
    tipo = TipoServicio.VACUNA

    def duracion(self) -> timedelta:
        return timedelta(minutes=15)


class ServicioCirugia(IServicioCita):
    tipo = TipoServicio.CIRUGIA

    def duracion(self) -> timedelta:
        return timedelta(minutes=120)


_REGISTRO: dict[TipoServicio, IServicioCita] = {
    s.tipo: s for s in (ServicioConsulta(), ServicioVacuna(), ServicioCirugia())
}


def registrar_servicio(servicio: IServicioCita) -> None:
    _REGISTRO[servicio.tipo] = servicio


def servicio_para(tipo: TipoServicio) -> IServicioCita:
    return _REGISTRO[tipo]
