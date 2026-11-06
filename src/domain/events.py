"""Domain Events (ADR-003)."""
from dataclasses import dataclass, field
from datetime import datetime


def _ahora() -> datetime:
    return datetime.now()


@dataclass(frozen=True)
class CitaAgendadaEvent:
    cita_id: str
    mascota_id: str
    veterinario_id: str
    tipo: str
    inicio: datetime
    celular_propietario: str | None = None
    ocurrido_en: datetime = field(default_factory=_ahora)


@dataclass(frozen=True)
class EmergenciaRegistradaEvent:
    cita_id: str
    mascota_id: str
    veterinario_id: str
    ocurrido_en: datetime = field(default_factory=_ahora)


@dataclass(frozen=True)
class CitaCambioEstadoEvent:
    cita_id: str
    estado_anterior: str
    estado_nuevo: str
    accion: str
    ocurrido_en: datetime = field(default_factory=_ahora)


@dataclass(frozen=True)
class PacienteInternadoEvent:
    mascota_id: str
    jaula: int
    ocupadas: int
    ocurrido_en: datetime = field(default_factory=_ahora)


@dataclass(frozen=True)
class CapacidadJaulasAlcanzadaEvent:
    ocupadas: int
    capacidad: int
    ocurrido_en: datetime = field(default_factory=_ahora)


@dataclass(frozen=True)
class NotaClinicaFirmadaEvent:
    nota_id: str
    mascota_id: str
    veterinario_id: str
    ocurrido_en: datetime = field(default_factory=_ahora)
