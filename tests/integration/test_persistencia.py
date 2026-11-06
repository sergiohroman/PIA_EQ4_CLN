"""Persistencia: bloqueo optimista (ADR-004), rollback del UoW y arranque con DB archivo."""
from datetime import datetime

import pytest

from src.api.container import Contenedor
from src.application.dtos import MascotaDto
from src.domain.exceptions import ConflictoDeConcurrencia
from src.infrastructure.database import normalizar_url

AHORA = datetime(2026, 11, 10, 8, 0)


def contenedor_con_dos_mascotas(tmp_path):
    c = Contenedor(f"sqlite:///{tmp_path / 'vetcare_test.db'}")
    c.expedientes.registrar_propietario("Ana", "8112345678")
    c.expedientes.registrar_mascota("8112345678", MascotaDto("Uno", "perro"))
    expediente = c.expedientes.registrar_mascota("8112345678", MascotaDto("Dos", "gato"))
    return c, [m.id for m in expediente.mascotas]


def test_dos_ingresos_simultaneos_detectan_conflicto_de_concurrencia(tmp_path):
    c, (uno, dos) = contenedor_con_dos_mascotas(tmp_path)
    with c.uow_factory() as u1, c.uow_factory() as u2:
        h1 = u1.hospitalizacion.obtener_actual()
        h2 = u2.hospitalizacion.obtener_actual()  # ambos leyeron la misma versión
        h1.ingresar_paciente(uno, "v", "x", AHORA)
        u1.hospitalizacion.save(h1)
        u1.commit()
        h2.ingresar_paciente(dos, "v", "x", AHORA)
        with pytest.raises(ConflictoDeConcurrencia):
            u2.hospitalizacion.save(h2)
    with c.uow_factory() as uow:
        assert uow.hospitalizacion.get_ocupacion_actual() == 1


def test_uow_hace_rollback_si_no_se_confirma(tmp_path):
    c, (uno, _) = contenedor_con_dos_mascotas(tmp_path)
    with c.uow_factory() as uow:
        h = uow.hospitalizacion.obtener_actual()
        h.ingresar_paciente(uno, "v", "x", AHORA)
        uow.hospitalizacion.save(h)  # sin commit
    with c.uow_factory() as uow:
        assert uow.hospitalizacion.get_ocupacion_actual() == 0


def test_los_datos_sobreviven_a_reiniciar_el_contenedor(tmp_path):
    c, _ = contenedor_con_dos_mascotas(tmp_path)
    c.engine.dispose()
    reiniciado = Contenedor(f"sqlite:///{tmp_path / 'vetcare_test.db'}")
    assert len(reiniciado.expedientes.obtener_expediente("8112345678").mascotas) == 2


@pytest.mark.parametrize(
    "entrada,esperada",
    [
        ("postgres://u:p@h:5432/db", "postgresql+psycopg2://u:p@h:5432/db"),
        ("postgresql://u:p@h/db", "postgresql+psycopg2://u:p@h/db"),
        ("sqlite:///x.db", "sqlite:///x.db"),
    ],
)
def test_normalizar_url_de_base_de_datos(entrada, esperada):
    assert normalizar_url(entrada) == esperada
