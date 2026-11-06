"""Esquemas Pydantic del contrato REST (se reflejan en OpenAPI/Swagger)."""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

TipoServicioLit = Literal["consulta", "vacuna", "cirugia"]


class ErrorOut(BaseModel):
    error: str = Field(examples=["CapacidadMaximaJaulasAlcanzada"])
    detalle: str = Field(examples=["Capacidad máxima de jaulas alcanzada"])


# ------------------------------------------------------------------ entrada
class VeterinarioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120, examples=["Dra. Laura López"])
    cedula: str = Field(min_length=1, max_length=40, examples=["CED-123456"])


class PropietarioIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120, examples=["Ana Martínez"])
    celular: str = Field(examples=["8112345678"], description="10 a 13 dígitos; único por propietario")


class MascotaIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120, examples=["Firulais"])
    especie: str = Field(min_length=1, max_length=60, examples=["perro"])
    raza: str = ""
    sexo: str = ""
    fecha_nacimiento: Optional[date] = None
    peso: Optional[Decimal] = Field(default=None, gt=0)
    alergias: list[str] = []


class ItemRecetaIn(BaseModel):
    medicamento: str = Field(examples=["Amoxicilina"])
    dosis: str = Field(examples=["1 tableta cada 12 h"])
    indicaciones: str = ""


class NotaIn(BaseModel):
    veterinario_id: str
    diagnostico: str = Field(min_length=1)
    notas: str = ""
    receta: list[ItemRecetaIn] = []
    peso: Optional[Decimal] = Field(default=None, gt=0)
    alergias: list[str] = []
    firmar: bool = Field(default=False, description="Equivale a 'Guardar y Firmar' (US-08)")


class NotaUpdateIn(BaseModel):
    diagnostico: Optional[str] = None
    notas: Optional[str] = None
    receta: Optional[list[ItemRecetaIn]] = None


class MascotaNotaIn(BaseModel):
    mascota: MascotaIn
    nota: NotaIn


class FirmaIn(BaseModel):
    veterinario_id: str


class FusionIn(BaseModel):
    origen_id: str = Field(description="Mascota duplicada que se elimina")
    destino_id: str = Field(description="Mascota que conserva el historial consolidado")


class CitaIn(BaseModel):
    mascota_id: str
    veterinario_id: str
    tipo: TipoServicioLit
    inicio: datetime = Field(examples=["2026-11-10T09:00:00"])

    @field_validator("inicio")
    @classmethod
    def _sin_zona(cls, valor: datetime) -> datetime:
        if valor.tzinfo is not None:
            raise ValueError("Use fecha y hora locales sin zona horaria (ej. 2026-11-10T09:00:00)")
        return valor


class EmergenciaIn(BaseModel):
    mascota_id: str
    veterinario_id: str


class TransicionIn(BaseModel):
    accion: Literal["aprobar", "completar", "cancelar"]


class IngresoIn(BaseModel):
    mascota_id: str
    veterinario_id: str
    motivo_ingreso: str = Field(min_length=1)


class SignosIn(BaseModel):
    mascota_id: str
    temperatura: Decimal = Field(examples=["38.5"])
    frecuencia_cardiaca: int
    frecuencia_respiratoria: int


class LineaOperacionIn(BaseModel):
    recurso_id: str
    precio: Decimal = Field(ge=0)
    cantidad: int = Field(gt=0)
    habilitado: bool = True


class EvaluarOperacionIn(BaseModel):
    operacion_id: str = "demo"
    actor_activo: bool
    actor_preferente: bool
    promocion_activa: bool = False
    autorizado: bool = True
    lineas: list[LineaOperacionIn] = []


# ------------------------------------------------------------------- salida
class VeterinarioOut(BaseModel):
    id: str
    nombre: str
    cedula: str
    activo: bool


class MascotaOut(BaseModel):
    id: str
    nombre: str
    especie: str
    raza: str
    sexo: str
    fecha_nacimiento: Optional[date]
    peso: Optional[Decimal]
    alergias: list[str]


class NotaOut(BaseModel):
    id: str
    mascota_id: str
    veterinario_id: str
    diagnostico: str
    notas: str
    receta: list[dict]
    estado: str
    firmada_por: Optional[str]
    sello: Optional[str]
    creada_en: datetime


class ExpedienteOut(BaseModel):
    propietario_id: str
    nombre: str
    celular: str
    mascotas: list[MascotaOut]
    notas: list[NotaOut]


class HistorialOut(BaseModel):
    mascota: MascotaOut
    propietario: str
    celular: str
    notas: list[NotaOut]


class CitaOut(BaseModel):
    id: str
    mascota_id: str
    veterinario_id: str
    tipo: str
    inicio: datetime
    fin: datetime
    estado: str
    es_emergencia: bool
    requiere_reprogramacion: bool


class EspacioOut(BaseModel):
    inicio: datetime
    fin: datetime


class RespuestaCitaOut(BaseModel):
    cita: CitaOut
    espacios_libres: list[EspacioOut]


class ConfirmacionOut(BaseModel):
    cita: CitaOut
    posicion_en_cola: int
    mensaje: str


class JaulaOut(BaseModel):
    numero: int
    estado: str
    mascota_id: Optional[str]


class EstadoJaulasOut(BaseModel):
    ocupadas: int
    disponibles: int
    capacidad: int
    porcentaje: float
    jaulas: list[JaulaOut]


class SignosPendienteOut(BaseModel):
    mascota_id: str
    jaula: int
    horas_desde_ultima_toma: float


class ProductividadOut(BaseModel):
    veterinario_id: str
    veterinario: str
    consultas: int
    vacunas: int
    cirugias: int
    total: int


class VacunaPendienteOut(BaseModel):
    cita_id: str
    mascota_id: str
    mascota: str
    especie: str
    propietario: str
    celular: str
    fecha_cita: datetime
    estado: str
    dias_atraso: int


class EvaluacionOut(BaseModel):
    operacion_id: str
    total_mxn: str
    puede_procesarse: bool
    beneficio_referencia: bool
    recursos_habilitados: bool
