import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app


class Reloj:
    """Reloj controlable para pruebas deterministas."""

    def __init__(self):
        self.valor = datetime(2026, 11, 10, 7, 0)

    def __call__(self) -> datetime:
        return self.valor


@pytest.fixture
def reloj():
    return Reloj()


@pytest.fixture
def client(reloj):
    """Por defecto SQLite en memoria; con TEST_DATABASE_URL se prueba contra PostgreSQL (Docker Compose)."""
    app = create_app(os.getenv("TEST_DATABASE_URL", "sqlite://"), ahora=reloj)
    with TestClient(app) as cliente:
        yield cliente
    from src.infrastructure.database import Base

    motor = app.state.contenedor.engine
    Base.metadata.drop_all(motor)  # aísla cada prueba también en PostgreSQL
    motor.dispose()


@pytest.fixture
def veterinario(client):
    respuesta = client.post("/veterinarios", json={"nombre": "Dra. López", "cedula": "CED-001"})
    assert respuesta.status_code == 201
    return respuesta.json()


@pytest.fixture
def nueva_mascota(client):
    """Crea (o reutiliza) un propietario y agrega una mascota; devuelve el id de la mascota."""

    def _crear(nombre="Firulais", celular="8112345678", propietario="Ana Martínez"):
        if client.get(f"/expedientes/{celular}").status_code == 404:
            assert client.post("/expedientes", json={"nombre": propietario, "celular": celular}).status_code == 201
        r = client.post(f"/expedientes/{celular}/mascotas", json={"nombre": nombre, "especie": "perro"})
        assert r.status_code == 201
        return r.json()["mascotas"][-1]["id"]

    return _crear
