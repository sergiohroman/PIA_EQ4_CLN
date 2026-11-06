"""Specifications compuestas contra el paquete de datos VetCare 24 (ZIP del PIA)."""
from decimal import Decimal
from pathlib import Path

import pytest

from src.application.evaluacion_reglas import (
    cargar_operaciones,
    ejecutar_casos,
    evaluar_operacion,
    simular_transicion,
)
from src.domain.exceptions import ValidacionDominio
from src.domain.operacion import LineaOperacion

DATOS = Path(__file__).resolve().parent.parent / "data" / "vetcare24"


def operaciones():
    return cargar_operaciones(DATOS)


def test_se_cargan_las_60_operaciones():
    assert len(operaciones()) == 60


def test_total_usa_decimal_exacto():
    # VET-O001: 3 x 881.00 (P009) + 4 x 1236.00 (P014)
    assert operaciones()["VET-O001"].total == Decimal("7587.00")


def test_actor_inactivo_no_puede_procesarse():
    assert not evaluar_operacion(operaciones()["VET-O006"])["puede_procesarse"]  # VET-C007 inactivo


def test_operacion_sin_detalle_no_puede_procesarse():
    assert operaciones()["VET-O013"].lineas == ()
    assert not evaluar_operacion(operaciones()["VET-O013"])["puede_procesarse"]


def test_operacion_no_autorizada_no_puede_procesarse():
    assert not evaluar_operacion(operaciones()["VET-O008"])["puede_procesarse"]


def test_operacion_valida_puede_procesarse():
    assert evaluar_operacion(operaciones()["VET-O001"])["puede_procesarse"]


def test_beneficio_requiere_preferente_total_y_sin_promocion():
    ops = operaciones()
    assert evaluar_operacion(ops["VET-O030"])["beneficio_referencia"]      # preferente, total alto, sin promo
    assert not evaluar_operacion(ops["VET-O001"])["beneficio_referencia"]  # no preferente
    assert not evaluar_operacion(ops["VET-O045"])["beneficio_referencia"]  # preferente pero con promoción


def test_beneficio_es_independiente_de_la_autorizacion():
    resultado = evaluar_operacion(operaciones()["VET-O040"])  # preferente, no autorizada
    assert resultado["beneficio_referencia"] and not resultado["puede_procesarse"]


def test_recurso_deshabilitado_se_detecta():
    assert not evaluar_operacion(operaciones()["VET-O005"])["recursos_habilitados"]  # incluye VET-P011
    assert evaluar_operacion(operaciones()["VET-O001"])["recursos_habilitados"]


@pytest.mark.parametrize("cantidad", [0, -1])
def test_cantidad_invalida(cantidad):
    with pytest.raises(ValidacionDominio):
        LineaOperacion("VET-P001", Decimal("313.00"), cantidad)


def test_precio_negativo_invalido():
    with pytest.raises(ValidacionDominio):
        LineaOperacion("VET-P001", Decimal("-1"), 1)


@pytest.mark.parametrize(
    "accion,estado,fragmento",
    [
        ("aprobar", "EN_ATENCION", "EVENTO"),
        ("cancelar", "CANCELADA", "EVENTO"),
        ("completar", "PROGRAMADA", "TransicionInvalida"),
        ("saltar_estado", "PROGRAMADA", "TransicionInvalida"),
        ("repetir_aprobacion", "EN_ATENCION", "TransicionInvalida"),
    ],
)
def test_simulacion_de_transiciones(accion, estado, fragmento):
    final, evidencia = simular_transicion(accion)
    assert final == estado and fragmento in evidencia


def test_ejecucion_completa_de_los_casos_del_paquete():
    casos, transiciones = ejecutar_casos(DATOS)
    assert len(casos) == 120 and len(transiciones) == 20
    assert all(c["resultado_alumno"] in ("CUMPLE", "NO_CUMPLE") for c in casos)
    assert all(t["evidencia"] for t in transiciones)
