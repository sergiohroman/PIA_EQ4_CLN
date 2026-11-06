"""Composition root: arma servicios, UoW, bus de eventos y notificaciones (inyección de dependencias)."""
from __future__ import annotations

from datetime import datetime
from typing import Callable

from src.application.event_bus import EventBus, registrar_handlers
from src.application.queries import (
    ConsultarHistorialMascotaHandler,
    ConsultarOcupacionJaulasHandler,
    ConsultarProductividadHandler,
    ConsultarVacunasPendientesHandler,
)
from src.application.services import (
    CitaApplicationService,
    ExpedienteApplicationService,
    HospitalizacionApplicationService,
    VeterinarioApplicationService,
)
from src.infrastructure.database import (
    crear_engine,
    crear_session_factory,
    inicializar_db,
)
from src.infrastructure.notificaciones import WhatsAppNotificacionService
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


class Contenedor:
    def __init__(self, database_url: str | None = None, ahora: Callable[[], datetime] = datetime.now):
        self.engine = crear_engine(database_url)
        inicializar_db(self.engine)
        self.session_factory = crear_session_factory(self.engine)
        self.notificaciones = WhatsAppNotificacionService()
        self.bus = EventBus()
        registrar_handlers(self.bus, self.notificaciones)

        def uow_factory() -> SqlAlchemyUnitOfWork:
            return SqlAlchemyUnitOfWork(self.session_factory, self.bus)

        self.uow_factory = uow_factory
        self.veterinarios = VeterinarioApplicationService(uow_factory)
        self.citas = CitaApplicationService(uow_factory, ahora)
        self.expedientes = ExpedienteApplicationService(uow_factory)
        self.hospitalizacion = HospitalizacionApplicationService(uow_factory, ahora)
        self.q_historial = ConsultarHistorialMascotaHandler(uow_factory)
        self.q_ocupacion = ConsultarOcupacionJaulasHandler(uow_factory)
        self.q_productividad = ConsultarProductividadHandler(uow_factory)
        self.q_vacunas_pendientes = ConsultarVacunasPendientesHandler(uow_factory, ahora)
