"""Puertos de persistencia: un repositorio por Aggregate Root (ADR-002).

El dominio solo conoce estas interfaces; las implementaciones viven en infrastructure.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from .agenda import Agenda, Cita
from .expediente import ExpedienteClinico
from .hospitalizacion import Hospitalizacion
from .value_objects import Celular
from .veterinario import Veterinario


class IExpedienteRepository(ABC):
    @abstractmethod
    def add(self, expediente: ExpedienteClinico) -> None: ...
    @abstractmethod
    def save(self, expediente: ExpedienteClinico) -> None: ...
    @abstractmethod
    def existe_celular(self, celular: Celular) -> bool: ...
    @abstractmethod
    def get_by_celular(self, celular: Celular) -> ExpedienteClinico | None: ...
    @abstractmethod
    def get_by_mascota_id(self, mascota_id: str) -> ExpedienteClinico | None: ...
    @abstractmethod
    def get_by_nota_id(self, nota_id: str) -> ExpedienteClinico | None: ...


class IAgendaRepository(ABC):
    @abstractmethod
    def get_by_fecha(self, fecha: date) -> Agenda: ...
    @abstractmethod
    def get_by_cita_id(self, cita_id: str) -> Agenda | None: ...
    @abstractmethod
    def save(self, agenda: Agenda) -> None: ...
    @abstractmethod
    def listar_rango(self, desde: date, hasta: date) -> list[Cita]: ...


class IHospitalizacionRepository(ABC):
    @abstractmethod
    def obtener_actual(self) -> Hospitalizacion: ...
    @abstractmethod
    def get_ocupacion_actual(self) -> int: ...
    @abstractmethod
    def save(self, hospitalizacion: Hospitalizacion) -> None: ...


class IVeterinarioRepository(ABC):
    @abstractmethod
    def add(self, veterinario: Veterinario) -> None: ...
    @abstractmethod
    def get(self, veterinario_id: str) -> Veterinario | None: ...
    @abstractmethod
    def listar(self) -> list[Veterinario]: ...
