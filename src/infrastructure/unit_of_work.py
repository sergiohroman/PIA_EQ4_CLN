"""Unit of Work SQLAlchemy: commit/rollback por caso de uso y publicación de eventos post-commit."""
from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from src.application.event_bus import EventBus
from src.application.unit_of_work import IUnitOfWork
from src.domain.exceptions import ConflictoDeConcurrencia, ConflictoDeNegocio

from .repositories import (
    SqlAgendaRepository,
    SqlExpedienteRepository,
    SqlHospitalizacionRepository,
    SqlVeterinarioRepository,
)


class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory, event_bus: EventBus):
        self._session_factory = session_factory
        self._bus = event_bus

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        self._vistos: list = []
        self.expedientes = SqlExpedienteRepository(self.session, self._vistos)
        self.agendas = SqlAgendaRepository(self.session, self._vistos)
        self.hospitalizacion = SqlHospitalizacionRepository(self.session, self._vistos)
        self.veterinarios = SqlVeterinarioRepository(self.session, self._vistos)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is not None:
                self.session.rollback()  # CU-04: rechazo => rollback completo
        finally:
            self.session.close()

    def commit(self) -> None:
        try:
            self.session.commit()
        except StaleDataError as error:
            self.session.rollback()
            raise ConflictoDeConcurrencia() from error
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictoDeNegocio("Conflicto de integridad en la base de datos") from error
        eventos = [e for agregado in self._vistos for e in agregado.pull_events()]
        self._bus.publish(eventos)

    def rollback(self) -> None:
        self.session.rollback()
