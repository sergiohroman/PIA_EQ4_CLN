"""Modelos de persistencia (SQLAlchemy 2.0). Son detalles de infraestructura: el dominio no los conoce."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class VeterinarioORM(Base):
    __tablename__ = "veterinarios"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    cedula: Mapped[str] = mapped_column(String(40), unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class PropietarioORM(Base):
    __tablename__ = "propietarios"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    celular: Mapped[str] = mapped_column(String(13), unique=True, index=True)  # N-004


class MascotaORM(Base):
    __tablename__ = "mascotas"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    propietario_id: Mapped[str] = mapped_column(ForeignKey("propietarios.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    especie: Mapped[str] = mapped_column(String(60))
    raza: Mapped[str] = mapped_column(String(60), default="")
    sexo: Mapped[str] = mapped_column(String(20), default="")
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    peso: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    alergias: Mapped[list] = mapped_column(JSON, default=list)


class NotaClinicaORM(Base):
    __tablename__ = "notas_clinicas"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    mascota_id: Mapped[str] = mapped_column(ForeignKey("mascotas.id"), index=True)
    veterinario_id: Mapped[str] = mapped_column(String(32))
    diagnostico: Mapped[str] = mapped_column(Text)
    notas: Mapped[str] = mapped_column(Text, default="")
    receta: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    estado: Mapped[str] = mapped_column(String(20))
    firma_id_usuario: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    firma_sello: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    firma_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    creada_en: Mapped[datetime] = mapped_column(DateTime)


class CitaORM(Base):
    __tablename__ = "citas"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, index=True)
    mascota_id: Mapped[str] = mapped_column(String(32), index=True)
    veterinario_id: Mapped[str] = mapped_column(String(32), index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    inicio: Mapped[datetime] = mapped_column(DateTime)
    fin: Mapped[datetime] = mapped_column(DateTime)
    estado: Mapped[str] = mapped_column(String(20))
    es_emergencia: Mapped[bool] = mapped_column(Boolean, default=False)
    requiere_reprogramacion: Mapped[bool] = mapped_column(Boolean, default=False)
    celular_propietario: Mapped[Optional[str]] = mapped_column(String(13), nullable=True)


class HospitalizacionORM(Base):
    """Fila única (id=1). `version` implementa el bloqueo optimista de ADR-004
    mediante comparar-y-actualizar (UPDATE ... WHERE version = :leida)."""

    __tablename__ = "hospitalizacion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    actualizado_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class JaulaORM(Base):
    __tablename__ = "jaulas"
    numero: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    mascota_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    veterinario_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ingreso: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class SignosVitalesORM(Base):
    __tablename__ = "signos_vitales"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mascota_id: Mapped[str] = mapped_column(String(32), index=True)
    temperatura: Mapped[Decimal] = mapped_column(Numeric(4, 1))
    frecuencia_cardiaca: Mapped[int] = mapped_column(Integer)
    frecuencia_respiratoria: Mapped[int] = mapped_column(Integer)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, index=True)
