"""ExpedienteClinico: US-04..US-08 (N-002, N-004, N-005)."""
from decimal import Decimal

import pytest

from src.domain.estados import NotaEstado
from src.domain.events import NotaClinicaFirmadaEvent
from src.domain.exceptions import (
    ClienteExistenteException,
    NoEncontrado,
    NotaFirmadaInmutable,
    TransicionInvalida,
    ValidacionDominio,
)
from src.domain.expediente import ExpedienteClinico, Mascota, Propietario
from src.domain.servicios_dominio import ValidadorDuplicidadClienteService
from src.domain.value_objects import Celular, ItemReceta, RecetaMedica
from src.domain.veterinario import Veterinario


def expediente():
    exp = ExpedienteClinico(Propietario("p1", "Ana", Celular("8112345678")))
    exp.registrar_mascota(Mascota("m1", "Firulais", "perro"))
    exp.registrar_mascota(Mascota("m2", "Firu", "perro", alergias=["penicilina"]))
    return exp


VET = Veterinario("v1", "Dra. López", "CED-123")


class RepoFalso:
    def __init__(self, existentes):
        self.existentes = existentes

    def existe_celular(self, celular):
        return celular.valor in self.existentes


def test_us04_alerta_cliente_existente():
    validador = ValidadorDuplicidadClienteService(RepoFalso({"8112345678"}))
    with pytest.raises(ClienteExistenteException):
        validador.validar_unico(Celular("81-1234-5678"))
    validador.validar_unico(Celular("8199999999"))


def test_us06_varias_mascotas_bajo_el_mismo_propietario():
    exp = expediente()
    exp.registrar_mascota(Mascota("m3", "Michi", "gato"))
    assert len(exp.mascotas) == 3
    with pytest.raises(ValidacionDominio):
        exp.registrar_mascota(Mascota("m3", "Otra", "gato"))


def test_mascota_valida_datos():
    with pytest.raises(ValidacionDominio):
        Mascota("m", "", "perro")
    with pytest.raises(ValidacionDominio):
        Mascota("m", "Rex", "perro", peso=0)


def test_us05_fusion_consolida_historial_y_elimina_duplicado():
    exp = expediente()
    exp.registrar_nota("n1", "m2", "v1", "Revisión general")
    destino = exp.fusionar_mascotas("m2", "m1")
    assert [m.id for m in exp.mascotas] == ["m1"]
    assert exp.obtener_nota("n1").mascota_id == "m1"
    assert destino.alergias == ["penicilina"]
    with pytest.raises(ValidacionDominio):
        exp.fusionar_mascotas("m1", "m1")
    with pytest.raises(NoEncontrado):
        exp.fusionar_mascotas("m1", "zzz")


def test_us07_nota_actualiza_peso_y_alergias():
    exp = expediente()
    receta = RecetaMedica((ItemReceta("Amoxicilina", "1 tableta c/12h"),))
    nota = exp.registrar_nota(
        "n1", "m1", "v1", "Otitis", "Limpieza", receta, peso=Decimal("12.5"), alergias=["polen"]
    )
    mascota = exp.obtener_mascota("m1")
    assert mascota.peso == Decimal("12.5") and mascota.alergias == ["polen"]
    assert nota.estado == NotaEstado.BORRADOR
    with pytest.raises(ValidacionDominio):
        exp.registrar_nota("n2", "m1", "v1", "  ")


def test_us08_firma_sella_y_bloquea_modificaciones():
    exp = expediente()
    exp.registrar_nota("n1", "m1", "v1", "Otitis")
    nota = exp.firmar_nota("n1", VET)
    assert nota.estado == NotaEstado.FIRMADA
    assert nota.firma.id_usuario == "v1" and len(nota.firma.sello) == 64
    assert isinstance(exp.pull_events()[0], NotaClinicaFirmadaEvent)
    with pytest.raises(NotaFirmadaInmutable):
        exp.modificar_nota("n1", diagnostico="otro")
    with pytest.raises(TransicionInvalida):
        exp.firmar_nota("n1", VET)


def test_nota_borrador_si_se_puede_editar_y_vet_inactivo_no_firma():
    exp = expediente()
    exp.registrar_nota("n1", "m1", "v1", "Otitis")
    exp.modificar_nota("n1", diagnostico="Otitis externa", notas="aplicar gotas")
    assert exp.obtener_nota("n1").diagnostico == "Otitis externa"
    with pytest.raises(ValidacionDominio):
        exp.firmar_nota("n1", Veterinario("v2", "Dr. X", "C-1", activo=False))


def test_historial_de_mascota():
    exp = expediente()
    exp.registrar_nota("n1", "m1", "v1", "A")
    exp.registrar_nota("n2", "m1", "v1", "B")
    assert [n.id for n in exp.historial("m1")] == ["n1", "n2"]
    with pytest.raises(NoEncontrado):
        exp.historial("zzz")
