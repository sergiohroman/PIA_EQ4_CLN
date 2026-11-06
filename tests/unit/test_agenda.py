"""Agenda: US-01, US-02, US-03 (N-001, N-007)."""
from datetime import date, datetime, timedelta

import pytest

from src.domain.agenda import Agenda
from src.domain.estados import CitaEstado
from src.domain.events import CitaAgendadaEvent, EmergenciaRegistradaEvent
from src.domain.exceptions import NoEncontrado, TraslapeDeCitas, TransicionInvalida, ValidacionDominio
from src.domain.servicios_dominio import AsignadorPrioridadEmergenciaService
from src.domain.value_objects import TipoServicio

FECHA = date(2026, 11, 10)


def hora(h, m=0):
    return datetime(2026, 11, 10, h, m)


def agenda_vacia():
    return Agenda(FECHA)


def test_us01_bloquea_tiempo_segun_tipo_de_servicio():
    ag = agenda_vacia()
    vacuna = ag.agendar_cita("c1", "m1", TipoServicio.VACUNA, "v1", hora(9))
    consulta = ag.agendar_cita("c2", "m2", TipoServicio.CONSULTA, "v1", hora(10))
    cirugia = ag.agendar_cita("c3", "m3", TipoServicio.CIRUGIA, "v1", hora(12))
    assert vacuna.fin - vacuna.inicio == timedelta(minutes=15)
    assert consulta.fin - consulta.inicio == timedelta(minutes=30)
    assert cirugia.fin - cirugia.inicio == timedelta(minutes=120)


def test_agendar_emite_evento_cita_agendada():
    ag = agenda_vacia()
    ag.agendar_cita("c1", "m1", TipoServicio.VACUNA, "v1", hora(9), celular_propietario="8112345678")
    eventos = ag.pull_events()
    assert len(eventos) == 1 and isinstance(eventos[0], CitaAgendadaEvent)
    assert eventos[0].celular_propietario == "8112345678"
    assert ag.pull_events() == []


def test_no_permite_traslape_del_mismo_veterinario():
    ag = agenda_vacia()
    ag.agendar_cita("c1", "m1", TipoServicio.CONSULTA, "v1", hora(9))
    with pytest.raises(TraslapeDeCitas):
        ag.agendar_cita("c2", "m2", TipoServicio.VACUNA, "v1", hora(9, 15))


def test_otro_veterinario_si_puede_en_el_mismo_horario():
    ag = agenda_vacia()
    ag.agendar_cita("c1", "m1", TipoServicio.CONSULTA, "v1", hora(9))
    ag.agendar_cita("c2", "m2", TipoServicio.CONSULTA, "v2", hora(9))
    assert len(ag.citas) == 2


def test_cita_cancelada_libera_el_horario():
    ag = agenda_vacia()
    ag.agendar_cita("c1", "m1", TipoServicio.CONSULTA, "v1", hora(9))
    ag.transicionar_cita("c1", "cancelar")
    ag.agendar_cita("c2", "m2", TipoServicio.CONSULTA, "v1", hora(9))
    assert ag.obtener("c1").estado == CitaEstado.CANCELADA


def test_fuera_de_horario_y_fecha_incorrecta():
    ag = agenda_vacia()
    with pytest.raises(ValidacionDominio):
        ag.agendar_cita("c1", "m1", TipoServicio.CONSULTA, "v1", hora(7))
    with pytest.raises(ValidacionDominio):
        ag.agendar_cita("c2", "m2", TipoServicio.CIRUGIA, "v1", hora(19))
    with pytest.raises(ValidacionDominio):
        ag.agendar_cita("c3", "m3", TipoServicio.CONSULTA, "v1", datetime(2026, 11, 11, 9))


def test_us02_espacios_libres_excluyen_citas_existentes():
    ag = agenda_vacia()
    ag.agendar_cita("c1", "m1", TipoServicio.CONSULTA, "v1", hora(8))
    libres = ag.espacios_libres("v1", TipoServicio.CONSULTA)
    inicios = [i for i, _ in libres]
    assert hora(8) not in inicios and hora(8, 15) not in inicios
    assert hora(8, 30) in inicios
    assert hora(19, 30) in inicios and hora(19, 45) not in inicios
    assert hora(8) in [i for i, _ in ag.espacios_libres("v2", TipoServicio.CONSULTA)]


def test_us03_emergencia_se_sobrepone_y_va_primero_en_la_cola():
    ag = agenda_vacia()
    regular = ag.agendar_cita("c1", "m1", TipoServicio.CONSULTA, "v1", hora(10))
    ag.pull_events()
    emergencia = AsignadorPrioridadEmergenciaService().registrar_emergencia(
        ag, "e1", "m9", "v1", hora(10, 10)
    )
    assert emergencia.es_emergencia
    assert regular.requiere_reprogramacion
    assert ag.cola_espera()[0].id == "e1"
    eventos = ag.pull_events()
    assert len(eventos) == 1 and isinstance(eventos[0], EmergenciaRegistradaEvent)


def test_emergencia_puede_registrarse_fuera_de_horario():
    ag = agenda_vacia()
    cita = ag.agendar_cita("e1", "m1", TipoServicio.CONSULTA, "v1", hora(23), es_emergencia=True)
    assert cita.es_emergencia


def test_transiciones_de_cita_en_la_agenda():
    ag = agenda_vacia()
    ag.agendar_cita("c1", "m1", TipoServicio.CONSULTA, "v1", hora(9))
    ag.transicionar_cita("c1", "aprobar")
    with pytest.raises(TransicionInvalida):
        ag.transicionar_cita("c1", "aprobar")
    ag.transicionar_cita("c1", "completar")
    assert ag.obtener("c1").estado == CitaEstado.COMPLETADA
    with pytest.raises(NoEncontrado):
        ag.obtener("no-existe")
