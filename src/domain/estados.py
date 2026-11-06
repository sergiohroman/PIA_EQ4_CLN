"""Máquinas de estado del dominio (ADR-006)."""
from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar

from .exceptions import TransicionInvalida

E = TypeVar("E", bound=Enum)


class StateMachine(Generic[E]):
    """Tabla de transiciones (estado, acción) -> estado siguiente."""

    def __init__(self, nombre: str, transiciones: dict[tuple[E, str], E]):
        self.nombre = nombre
        self._transiciones = dict(transiciones)

    def siguiente(self, estado: E, accion: str) -> E:
        try:
            return self._transiciones[(estado, accion)]
        except KeyError:
            raise TransicionInvalida(
                f"{self.nombre}: no se puede '{accion}' cuando el estado es {estado.value}"
            ) from None

    def acciones_permitidas(self, estado: E) -> list[str]:
        return sorted(a for (e, a) in self._transiciones if e == estado)


class CitaEstado(str, Enum):
    PROGRAMADA = "PROGRAMADA"
    EN_ATENCION = "EN_ATENCION"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"


MAQUINA_CITA: StateMachine[CitaEstado] = StateMachine(
    "Cita",
    {
        (CitaEstado.PROGRAMADA, "aprobar"): CitaEstado.EN_ATENCION,
        (CitaEstado.EN_ATENCION, "completar"): CitaEstado.COMPLETADA,
        (CitaEstado.PROGRAMADA, "cancelar"): CitaEstado.CANCELADA,
        (CitaEstado.EN_ATENCION, "cancelar"): CitaEstado.CANCELADA,
    },
)


class NotaEstado(str, Enum):
    BORRADOR = "BORRADOR"
    FIRMADA = "FIRMADA"


MAQUINA_NOTA: StateMachine[NotaEstado] = StateMachine(
    "NotaClinica",
    {(NotaEstado.BORRADOR, "firmar"): NotaEstado.FIRMADA},
)
