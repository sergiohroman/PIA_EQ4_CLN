"""DTOs de entrada/salida de los Application Services (Etapa 4 de la Act. 3)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from src.domain.agenda import Cita
from src.domain.expediente import ExpedienteClinico, Mascota, NotaClinica
from src.domain.hospitalizacion import Hospitalizacion, Jaula


# ---- entrada -----------------------------------------------------------
@dataclass(frozen=True)
class SolicitudCitaDto:
    mascota_id: str
    veterinario_id: str
    tipo: str
    inicio: datetime


@dataclass(frozen=True)
class EmergenciaDto:
    mascota_id: str
    veterinario_id: str


@dataclass(frozen=True)
class MascotaDto:
    nombre: str
    especie: str
    raza: str = ""
    sexo: str = ""
    fecha_nacimiento: date | None = None
    peso: Decimal | None = None
    alergias: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ItemRecetaDto:
    medicamento: str
    dosis: str
    indicaciones: str = ""


@dataclass(frozen=True)
class NotaDto:
    veterinario_id: str
    diagnostico: str
    notas: str = ""
    receta: list[ItemRecetaDto] = field(default_factory=list)
    peso: Decimal | None = None
    alergias: list[str] = field(default_factory=list)
    firmar: bool = False


@dataclass(frozen=True)
class MascotaNotaDto:
    """CU-03: vincular mascota a cliente existente y guardar nota médica."""

    mascota: MascotaDto
    nota: NotaDto


@dataclass(frozen=True)
class IngresoInternadoDto:
    mascota_id: str
    veterinario_id: str
    motivo_ingreso: str


@dataclass(frozen=True)
class SignosVitalesDto:
    mascota_id: str
    temperatura: Decimal
    frecuencia_cardiaca: int
    frecuencia_respiratoria: int


# ---- salida ------------------------------------------------------------
@dataclass
class CitaDto:
    id: str
    mascota_id: str
    veterinario_id: str
    tipo: str
    inicio: datetime
    fin: datetime
    estado: str
    es_emergencia: bool
    requiere_reprogramacion: bool

    @classmethod
    def desde(cls, c: Cita) -> "CitaDto":
        return cls(c.id, c.mascota_id, c.veterinario_id, c.tipo.value, c.inicio, c.fin,
                   c.estado.value, c.es_emergencia, c.requiere_reprogramacion)


@dataclass
class RespuestaCitaDto:
    cita: CitaDto
    espacios_libres: list[dict]


@dataclass
class ConfirmacionDto:
    cita: CitaDto
    posicion_en_cola: int
    mensaje: str


@dataclass
class MascotaSalidaDto:
    id: str
    nombre: str
    especie: str
    raza: str
    sexo: str
    fecha_nacimiento: date | None
    peso: Decimal | None
    alergias: list[str]

    @classmethod
    def desde(cls, m: Mascota) -> "MascotaSalidaDto":
        return cls(m.id, m.nombre, m.especie, m.raza, m.sexo, m.fecha_nacimiento, m.peso, list(m.alergias))


@dataclass
class NotaSalidaDto:
    id: str
    mascota_id: str
    veterinario_id: str
    diagnostico: str
    notas: str
    receta: list[dict]
    estado: str
    firmada_por: str | None
    sello: str | None
    creada_en: datetime

    @classmethod
    def desde(cls, n: NotaClinica) -> "NotaSalidaDto":
        return cls(n.id, n.mascota_id, n.veterinario_id, n.diagnostico, n.notas,
                   n.receta.a_lista() if n.receta else [], n.estado.value,
                   n.firma.id_usuario if n.firma else None, n.firma.sello if n.firma else None,
                   n.creada_en)


@dataclass
class ExpedienteDto:
    propietario_id: str
    nombre: str
    celular: str
    mascotas: list[MascotaSalidaDto]
    notas: list[NotaSalidaDto]

    @classmethod
    def desde(cls, e: ExpedienteClinico) -> "ExpedienteDto":
        return cls(e.propietario.id, e.propietario.nombre, e.propietario.celular.valor,
                   [MascotaSalidaDto.desde(m) for m in e.mascotas],
                   [NotaSalidaDto.desde(n) for n in e.notas])


@dataclass
class JaulaDto:
    numero: int
    estado: str
    mascota_id: str | None

    @classmethod
    def desde(cls, j: Jaula) -> "JaulaDto":
        return cls(j.numero, j.estado, j.mascota_id)


@dataclass
class EstadoJaulasDto:
    ocupadas: int
    disponibles: int
    capacidad: int
    porcentaje: float
    jaulas: list[JaulaDto]

    @classmethod
    def desde(cls, h: Hospitalizacion) -> "EstadoJaulasDto":
        o = h.ocupacion()
        return cls(o["ocupadas"], o["disponibles"], o["capacidad"], o["porcentaje"],
                   [JaulaDto.desde(j) for j in h.jaulas])


@dataclass
class HistorialMascotaDto:
    mascota: MascotaSalidaDto
    propietario: str
    celular: str
    notas: list[NotaSalidaDto]
