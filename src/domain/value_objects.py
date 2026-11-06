"""Value Objects del dominio VetCare 24 (sin identidad, inmutables)."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum

from .exceptions import ValidacionDominio


class TipoServicio(str, Enum):
    """Tipo de atención (N-001). La duración la entrega IServicioCita."""

    CONSULTA = "consulta"
    VACUNA = "vacuna"
    CIRUGIA = "cirugia"


@dataclass(frozen=True)
class Celular:
    """Identificador único del propietario (N-002, N-004)."""

    valor: str

    def __post_init__(self) -> None:
        limpio = re.sub(r"[\s\-()+]", "", self.valor or "")
        if not re.fullmatch(r"\d{10,13}", limpio):
            raise ValidacionDominio("El celular debe contener entre 10 y 13 dígitos")
        object.__setattr__(self, "valor", limpio)

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class SignosVitales:
    """Lectura inmutable de signos vitales; un cambio crea otra lectura (US-11)."""

    temperatura: Decimal
    frecuencia_cardiaca: int
    frecuencia_respiratoria: int
    fecha_registro: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        try:
            temp = Decimal(str(self.temperatura))
        except InvalidOperation as exc:
            raise ValidacionDominio("Temperatura inválida") from exc
        object.__setattr__(self, "temperatura", temp)
        if not Decimal("30") <= temp <= Decimal("45"):
            raise ValidacionDominio("Temperatura fuera de rango (30-45 °C)")
        if not 20 <= self.frecuencia_cardiaca <= 300:
            raise ValidacionDominio("Frecuencia cardiaca fuera de rango (20-300 lpm)")
        if not 5 <= self.frecuencia_respiratoria <= 120:
            raise ValidacionDominio("Frecuencia respiratoria fuera de rango (5-120 rpm)")


@dataclass(frozen=True)
class ItemReceta:
    medicamento: str
    dosis: str
    indicaciones: str = ""

    def __post_init__(self) -> None:
        if not self.medicamento.strip() or not self.dosis.strip():
            raise ValidacionDominio("Cada medicamento requiere nombre y dosis")


@dataclass(frozen=True)
class RecetaMedica:
    items: tuple[ItemReceta, ...]

    def __post_init__(self) -> None:
        if not self.items:
            raise ValidacionDominio("La receta debe incluir al menos un medicamento")

    def a_lista(self) -> list[dict]:
        return [
            {"medicamento": i.medicamento, "dosis": i.dosis, "indicaciones": i.indicaciones}
            for i in self.items
        ]

    @classmethod
    def desde_lista(cls, datos: list[dict]) -> "RecetaMedica":
        return cls(tuple(ItemReceta(**d) for d in datos))


@dataclass(frozen=True)
class FirmaDigital:
    """Sello que valida el usuario veterinario sobre una nota (N-005, US-08)."""

    id_usuario: str
    sello: str
    firmado_en: datetime

    @classmethod
    def crear(cls, id_usuario: str, contenido: str, ahora: datetime | None = None) -> "FirmaDigital":
        ahora = ahora or datetime.now()
        huella = hashlib.sha256(f"{id_usuario}|{ahora.isoformat()}|{contenido}".encode()).hexdigest()
        return cls(id_usuario=id_usuario, sello=huella, firmado_en=ahora)
