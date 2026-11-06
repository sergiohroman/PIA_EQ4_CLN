"""Specification: composición AND / OR / NOT (ADR-005)."""
from src.domain.specification import Specification


class Siempre(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return True


class Nunca(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return False


def test_and_or_not_metodos():
    assert Siempre().and_(Siempre()).is_satisfied_by(1)
    assert not Siempre().and_(Nunca()).is_satisfied_by(1)
    assert Nunca().or_(Siempre()).is_satisfied_by(1)
    assert not Nunca().or_(Nunca()).is_satisfied_by(1)
    assert Nunca().not_().is_satisfied_by(1)


def test_operadores_sobrecargados_y_composicion_anidada():
    regla = (Siempre() & ~Nunca()) | Nunca()
    assert regla.is_satisfied_by("x")
    assert not (Siempre() & Nunca() & Siempre()).is_satisfied_by("x")


# ---- US-13: vacuna atrasada (Specification compuesta) ----------------------
from datetime import datetime as _dt  # noqa: E402

import pytest as _pytest  # noqa: E402

from src.domain.agenda import Cita as _Cita  # noqa: E402
from src.domain.estados import CitaEstado as _Estado  # noqa: E402
from src.domain.specifications import vacuna_atrasada as _vacuna_atrasada  # noqa: E402
from src.domain.value_objects import TipoServicio as _Tipo  # noqa: E402


@_pytest.mark.parametrize(
    "tipo,estado,inicio,esperado",
    [
        (_Tipo.VACUNA, _Estado.PROGRAMADA, _dt(2026, 11, 10, 9), True),   # no asistió
        (_Tipo.VACUNA, _Estado.CANCELADA, _dt(2026, 11, 10, 9), True),    # canceló y no reagendó
        (_Tipo.VACUNA, _Estado.COMPLETADA, _dt(2026, 11, 10, 9), False),  # ya se aplicó
        (_Tipo.VACUNA, _Estado.EN_ATENCION, _dt(2026, 11, 10, 9), False), # se está aplicando
        (_Tipo.VACUNA, _Estado.PROGRAMADA, _dt(2026, 11, 13, 9), False),  # aún no vence
        (_Tipo.CONSULTA, _Estado.PROGRAMADA, _dt(2026, 11, 10, 9), False),  # no es vacuna
    ],
)
def test_us13_vacuna_atrasada(tipo, estado, inicio, esperado):
    cita = _Cita("c1", "m1", "v1", tipo, inicio, inicio, estado=estado)
    assert _vacuna_atrasada(_dt(2026, 11, 12, 9)).is_satisfied_by(cita) is esperado
