"""Configuración de base de datos. Todo viene de variables de entorno (12-Factor)."""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def normalizar_url(url: str) -> str:
    """Railway/Render entregan postgres:// o postgresql://; SQLAlchemy necesita el driver."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


def obtener_url() -> str:
    return normalizar_url(os.getenv("DATABASE_URL", "sqlite:///./vetcare.db"))


def crear_engine(url: str | None = None) -> Engine:
    url = normalizar_url(url or obtener_url())
    if url.startswith("sqlite"):
        opciones: dict = {"connect_args": {"check_same_thread": False}}
        if url in ("sqlite://", "sqlite:///:memory:"):
            opciones["poolclass"] = StaticPool
        return create_engine(url, **opciones)
    return create_engine(url, pool_pre_ping=True)


def crear_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)


def inicializar_db(engine: Engine) -> None:
    """Crea tablas y las 10 jaulas físicas (BR-002)."""
    from . import orm  # noqa: F401  (registra los modelos en Base.metadata)
    from src.domain.hospitalizacion import CAPACIDAD_MAXIMA

    Base.metadata.create_all(engine)
    with Session(engine) as sesion:
        if sesion.get(orm.HospitalizacionORM, 1) is None:
            sesion.add(orm.HospitalizacionORM(id=1))
            for numero in range(1, CAPACIDAD_MAXIMA + 1):
                sesion.add(orm.JaulaORM(numero=numero))
            sesion.commit()
