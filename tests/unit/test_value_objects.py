from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.exceptions import ValidacionDominio
from src.domain.value_objects import Celular, FirmaDigital, ItemReceta, RecetaMedica, SignosVitales


def test_celular_se_normaliza():
    assert Celular("81 1234-5678").valor == "8112345678"


@pytest.mark.parametrize("valor", ["", "abc", "123", "81123456789012345"])
def test_celular_invalido(valor):
    with pytest.raises(ValidacionDominio):
        Celular(valor)


def test_signos_vitales_validos_y_decimal():
    s = SignosVitales(38.5, 100, 30)
    assert s.temperatura == Decimal("38.5")


@pytest.mark.parametrize("temp,fc,fr", [(20, 100, 30), (38, 5, 30), (38, 100, 500)])
def test_signos_vitales_fuera_de_rango(temp, fc, fr):
    with pytest.raises(ValidacionDominio):
        SignosVitales(temp, fc, fr)


def test_receta_requiere_items_y_roundtrip():
    with pytest.raises(ValidacionDominio):
        RecetaMedica(())
    with pytest.raises(ValidacionDominio):
        ItemReceta("", "1 tableta")
    receta = RecetaMedica((ItemReceta("Amoxicilina", "1 tableta c/12h", "7 días"),))
    assert RecetaMedica.desde_lista(receta.a_lista()) == receta


def test_firma_digital_determinista_por_contenido():
    ahora = datetime(2026, 11, 5, 10, 0)
    a = FirmaDigital.crear("VET-1", "contenido", ahora)
    b = FirmaDigital.crear("VET-1", "contenido", ahora)
    c = FirmaDigital.crear("VET-1", "otro", ahora)
    assert a.sello == b.sello != c.sello
