"""Modelo de evaluación de reglas del paquete VetCare 24 (adaptador de pruebas).

El ZIP del PIA propone reglas ilustrativas (`puede_procesarse`, `beneficio_referencia`)
sobre operaciones con importes en MXN. Se modelan aquí como Specifications compuestas
para demostrar AND/OR/NOT sin reemplazar las reglas propias del BRD (ver ADR-005).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .exceptions import ValidacionDominio
from .specification import Specification
from .specifications import (
    ActorActivo,
    ActorPreferente,
    OperacionAutorizada,
    OperacionConDetalle,
    PromocionActiva,
    RecursosHabilitados,
    TotalMinimo,
)

UMBRAL_BENEFICIO_MXN = Decimal("1500")


@dataclass(frozen=True)
class LineaOperacion:
    recurso_id: str
    precio: Decimal
    cantidad: int
    habilitado: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "precio", Decimal(str(self.precio)))
        if self.cantidad <= 0:
            raise ValidacionDominio("La cantidad debe ser mayor a cero")
        if self.precio < 0:
            raise ValidacionDominio("El precio no puede ser negativo")

    @property
    def subtotal(self) -> Decimal:
        return self.precio * self.cantidad


@dataclass(frozen=True)
class OperacionVeterinaria:
    operacion_id: str
    actor_id: str
    actor_activo: bool
    actor_preferente: bool
    lineas: tuple[LineaOperacion, ...]
    promocion_activa: bool = False
    autorizado: bool = True

    @property
    def total(self) -> Decimal:
        return sum((l.subtotal for l in self.lineas), Decimal("0"))


def puede_procesarse() -> Specification:
    """actor activo AND operación con al menos una línea AND autorización."""
    return ActorActivo() & OperacionConDetalle() & OperacionAutorizada()


def beneficio_referencia() -> Specification:
    """actor preferente AND total >= 1500 MXN AND NOT promoción activa."""
    return ActorPreferente() & TotalMinimo(UMBRAL_BENEFICIO_MXN) & ~PromocionActiva()


def recursos_habilitados() -> Specification:
    return RecursosHabilitados()
