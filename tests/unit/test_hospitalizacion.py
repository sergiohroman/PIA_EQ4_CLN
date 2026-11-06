"""Hospitalizacion: US-11, US-12 (N-006, BR-002)."""
from datetime import datetime, timedelta

import pytest

from src.domain.events import CapacidadJaulasAlcanzadaEvent, PacienteInternadoEvent
from src.domain.exceptions import (
    CapacidadMaximaJaulasAlcanzada,
    PacienteNoInternado,
    PacienteYaInternado,
)
from src.domain.hospitalizacion import Hospitalizacion
from src.domain.value_objects import SignosVitales

T0 = datetime(2026, 11, 10, 8, 0)


def llenar(h, n):
    for i in range(n):
        h.ingresar_paciente(f"m{i}", "v1", "observación", T0)


def test_us12_rechaza_el_ingreso_numero_once():
    h = Hospitalizacion()
    llenar(h, 10)
    assert h.ocupadas() == 10
    with pytest.raises(CapacidadMaximaJaulasAlcanzada) as error:
        h.ingresar_paciente("m11", "v1", "x", T0)
    assert "Capacidad máxima de jaulas alcanzada" in str(error.value)
    assert h.ocupadas() == 10


def test_ingreso_asigna_jaula_y_emite_eventos():
    h = Hospitalizacion()
    jaula = h.ingresar_paciente("m1", "v1", "cirugía", T0)
    assert jaula.numero == 1 and jaula.estado == "Ocupada"
    eventos = h.pull_events()
    assert len(eventos) == 1 and isinstance(eventos[0], PacienteInternadoEvent)


def test_al_llegar_a_diez_se_emite_capacidad_alcanzada():
    h = Hospitalizacion()
    llenar(h, 10)
    tipos = [type(e) for e in h.pull_events()]
    assert tipos.count(PacienteInternadoEvent) == 10
    assert tipos.count(CapacidadJaulasAlcanzadaEvent) == 1


def test_alta_libera_jaula_y_permite_nuevo_ingreso():
    h = Hospitalizacion()
    llenar(h, 10)
    h.dar_alta("m3")
    assert h.ocupadas() == 9
    h.ingresar_paciente("m99", "v1", "x", T0)
    assert h.ocupadas() == 10


def test_no_permite_doble_ingreso_ni_alta_de_no_internado():
    h = Hospitalizacion()
    h.ingresar_paciente("m1", "v1", "x", T0)
    with pytest.raises(PacienteYaInternado):
        h.ingresar_paciente("m1", "v1", "x", T0)
    with pytest.raises(PacienteNoInternado):
        h.dar_alta("otra")


def test_ocupacion_us15():
    h = Hospitalizacion()
    llenar(h, 8)
    assert h.ocupacion() == {"ocupadas": 8, "disponibles": 2, "capacidad": 10, "porcentaje": 80.0}


def test_us11_signos_pendientes_despues_de_4_horas():
    h = Hospitalizacion()
    h.ingresar_paciente("m1", "v1", "x", T0)
    assert h.signos_pendientes(T0 + timedelta(hours=3, minutes=59)) == []
    pendientes = h.signos_pendientes(T0 + timedelta(hours=4))
    assert pendientes[0]["mascota_id"] == "m1"
    h.registrar_signos("m1", SignosVitales(38.5, 100, 30, T0 + timedelta(hours=4)))
    assert h.signos_pendientes(T0 + timedelta(hours=5)) == []
    assert len(h.pull_signos_nuevos()) == 1 and h.pull_signos_nuevos() == []


def test_signos_requieren_paciente_internado():
    h = Hospitalizacion()
    with pytest.raises(PacienteNoInternado):
        h.registrar_signos("m1", SignosVitales(38.5, 100, 30))
