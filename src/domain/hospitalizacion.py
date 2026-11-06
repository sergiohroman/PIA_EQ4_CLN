"""Aggregate Hospitalizacion (N-006, BR-002). Regla de oro: nunca más de 10 jaulas ocupadas."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .base import AggregateRoot
from .events import CapacidadJaulasAlcanzadaEvent, PacienteInternadoEvent
from .exceptions import (
    CapacidadMaximaJaulasAlcanzada,
    PacienteNoInternado,
    PacienteYaInternado,
)
from .specifications import HospitalizacionTieneCupo
from .value_objects import SignosVitales

CAPACIDAD_MAXIMA = 10


@dataclass
class Jaula:
    numero: int
    mascota_id: str | None = None
    veterinario_id: str | None = None
    motivo: str | None = None
    ingreso: datetime | None = None

    @property
    def ocupada(self) -> bool:
        return self.mascota_id is not None

    @property
    def estado(self) -> str:
        return "Ocupada" if self.ocupada else "Disponible"


class Hospitalizacion(AggregateRoot):
    def __init__(
        self,
        jaulas: list[Jaula] | None = None,
        signos: dict[str, list[SignosVitales]] | None = None,
        version: int = 0,
    ):
        super().__init__()
        self.jaulas = jaulas or [Jaula(n) for n in range(1, CAPACIDAD_MAXIMA + 1)]
        self._signos: dict[str, list[SignosVitales]] = {k: list(v) for k, v in (signos or {}).items()}
        self._signos_nuevos: list[tuple[str, SignosVitales]] = []
        self.version = version

    @property
    def capacidad(self) -> int:
        return len(self.jaulas)

    def ocupadas(self) -> int:
        return sum(1 for j in self.jaulas if j.ocupada)

    def ocupacion(self) -> dict:
        ocupadas = self.ocupadas()
        return {
            "ocupadas": ocupadas,
            "disponibles": self.capacidad - ocupadas,
            "capacidad": self.capacidad,
            "porcentaje": round(100 * ocupadas / self.capacidad, 1),
        }

    def _jaula_de(self, mascota_id: str) -> Jaula | None:
        return next((j for j in self.jaulas if j.mascota_id == mascota_id), None)

    def ingresar_paciente(
        self,
        mascota_id: str,
        veterinario_id: str,
        motivo: str,
        ahora: datetime | None = None,
    ) -> Jaula:
        if self._jaula_de(mascota_id) is not None:
            raise PacienteYaInternado()
        if not HospitalizacionTieneCupo().is_satisfied_by(self):
            raise CapacidadMaximaJaulasAlcanzada()
        jaula = next(j for j in self.jaulas if not j.ocupada)
        jaula.mascota_id = mascota_id
        jaula.veterinario_id = veterinario_id
        jaula.motivo = motivo
        jaula.ingreso = ahora or datetime.now()
        ocupadas = self.ocupadas()
        self._registrar(PacienteInternadoEvent(mascota_id, jaula.numero, ocupadas))
        if ocupadas == self.capacidad:
            self._registrar(CapacidadJaulasAlcanzadaEvent(ocupadas, self.capacidad))
        return jaula

    def dar_alta(self, mascota_id: str) -> Jaula:
        jaula = self._jaula_de(mascota_id)
        if jaula is None:
            raise PacienteNoInternado()
        jaula.mascota_id = jaula.veterinario_id = jaula.motivo = jaula.ingreso = None
        self._signos.pop(mascota_id, None)
        return jaula

    def registrar_signos(self, mascota_id: str, signos: SignosVitales) -> None:
        if self._jaula_de(mascota_id) is None:
            raise PacienteNoInternado()
        self._signos.setdefault(mascota_id, []).append(signos)
        self._signos_nuevos.append((mascota_id, signos))

    def signos_de(self, mascota_id: str) -> list[SignosVitales]:
        return sorted(self._signos.get(mascota_id, []), key=lambda s: s.fecha_registro)

    def signos_pendientes(self, ahora: datetime, horas: int = 4) -> list[dict]:
        """US-11: pacientes cuya última toma (o ingreso) supera `horas`."""
        pendientes = []
        for jaula in self.jaulas:
            if not jaula.ocupada:
                continue
            lecturas = self.signos_de(jaula.mascota_id)
            referencia = lecturas[-1].fecha_registro if lecturas else jaula.ingreso
            transcurrido = ahora - referencia
            if transcurrido >= timedelta(hours=horas):
                pendientes.append(
                    {
                        "mascota_id": jaula.mascota_id,
                        "jaula": jaula.numero,
                        "horas_desde_ultima_toma": round(transcurrido.total_seconds() / 3600, 1),
                    }
                )
        return pendientes

    def pull_signos_nuevos(self) -> list[tuple[str, SignosVitales]]:
        nuevos, self._signos_nuevos = self._signos_nuevos, []
        return nuevos
