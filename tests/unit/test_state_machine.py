"""State Machine de Cita (ADR-006). Cubre los escenarios de transiciones_prueba.csv."""
import pytest

from src.domain.estados import MAQUINA_CITA, CitaEstado
from src.domain.exceptions import TransicionInvalida


def test_flujo_feliz():
    estado = MAQUINA_CITA.siguiente(CitaEstado.PROGRAMADA, "aprobar")
    assert estado == CitaEstado.EN_ATENCION
    assert MAQUINA_CITA.siguiente(estado, "completar") == CitaEstado.COMPLETADA


@pytest.mark.parametrize("estado", [CitaEstado.PROGRAMADA, CitaEstado.EN_ATENCION])
def test_cancelacion_permitida(estado):
    assert MAQUINA_CITA.siguiente(estado, "cancelar") == CitaEstado.CANCELADA


def test_repetir_aprobacion_es_invalido():
    with pytest.raises(TransicionInvalida):
        MAQUINA_CITA.siguiente(CitaEstado.EN_ATENCION, "aprobar")


def test_saltar_estado_es_invalido():
    with pytest.raises(TransicionInvalida):
        MAQUINA_CITA.siguiente(CitaEstado.PROGRAMADA, "completar")


@pytest.mark.parametrize("estado", [CitaEstado.COMPLETADA, CitaEstado.CANCELADA])
def test_estados_terminales_no_aceptan_acciones(estado):
    assert MAQUINA_CITA.acciones_permitidas(estado) == []
    for accion in ("aprobar", "completar", "cancelar"):
        with pytest.raises(TransicionInvalida):
            MAQUINA_CITA.siguiente(estado, accion)


def test_acciones_permitidas():
    assert MAQUINA_CITA.acciones_permitidas(CitaEstado.PROGRAMADA) == ["aprobar", "cancelar"]
