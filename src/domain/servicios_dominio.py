"""Domain Services (lógica que no pertenece a una sola entidad)."""
from __future__ import annotations

from datetime import datetime

from .agenda import Agenda, Cita
from .exceptions import ClienteExistenteException
from .repositories import IExpedienteRepository
from .specifications import CelularNoRegistrado
from .value_objects import Celular, TipoServicio


class ValidadorDuplicidadClienteService:
    """N-004 / US-04: unicidad del celular antes de crear un propietario."""

    def __init__(self, expedientes: IExpedienteRepository):
        self._expedientes = expedientes

    def validar_unico(self, celular: Celular) -> None:
        regla = CelularNoRegistrado(self._expedientes.existe_celular)
        if not regla.is_satisfied_by(celular):
            raise ClienteExistenteException(
                "Cliente existente: ya hay un propietario con ese celular; abra el perfil actual"
            )


class AsignadorPrioridadEmergenciaService:
    """N-007 / US-03: coordina Agenda (desplazar citas) y alerta al Veterinario."""

    def registrar_emergencia(
        self,
        agenda: Agenda,
        cita_id: str,
        mascota_id: str,
        veterinario_id: str,
        ahora: datetime,
        celular_propietario: str | None = None,
    ) -> Cita:
        return agenda.agendar_cita(
            cita_id=cita_id,
            mascota_id=mascota_id,
            tipo=TipoServicio.CONSULTA,
            veterinario_id=veterinario_id,
            inicio=ahora,
            celular_propietario=celular_propietario,
            es_emergencia=True,
        )
