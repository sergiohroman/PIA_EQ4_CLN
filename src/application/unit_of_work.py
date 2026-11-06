"""Puerto Unit of Work (ADR-002): una transacción de negocio por caso de uso."""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.repositories import (
    IAgendaRepository,
    IExpedienteRepository,
    IHospitalizacionRepository,
    IVeterinarioRepository,
)


class IUnitOfWork(ABC):
    expedientes: IExpedienteRepository
    agendas: IAgendaRepository
    hospitalizacion: IHospitalizacionRepository
    veterinarios: IVeterinarioRepository

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> None: ...

    @abstractmethod
    def commit(self) -> None:
        """Persiste cambios y publica los Domain Events DESPUÉS del commit."""

    @abstractmethod
    def rollback(self) -> None: ...
