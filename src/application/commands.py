"""Lado de escritura de CQRS (Etapa 6). Los Handlers delegan en los Application Services."""
from __future__ import annotations

from dataclasses import dataclass

from .dtos import EstadoJaulasDto, IngresoInternadoDto, NotaDto, NotaSalidaDto
from .services import ExpedienteApplicationService, HospitalizacionApplicationService


@dataclass(frozen=True)
class RegistrarIngresoHospitalizacionCommand:
    mascota_id: str
    veterinario_id: str
    motivo_ingreso: str


class RegistrarIngresoHospitalizacionHandler:
    def __init__(self, servicio: HospitalizacionApplicationService):
        self._servicio = servicio

    def handle(self, comando: RegistrarIngresoHospitalizacionCommand) -> EstadoJaulasDto:
        return self._servicio.ingresar_paciente(
            IngresoInternadoDto(comando.mascota_id, comando.veterinario_id, comando.motivo_ingreso)
        )


@dataclass(frozen=True)
class GuardarNotaClinicaCommand:
    mascota_id: str
    nota: NotaDto


class GuardarNotaClinicaHandler:
    def __init__(self, servicio: ExpedienteApplicationService):
        self._servicio = servicio

    def handle(self, comando: GuardarNotaClinicaCommand) -> NotaSalidaDto:
        return self._servicio.guardar_nota(comando.mascota_id, comando.nota)
