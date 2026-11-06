"""Bus de eventos síncrono. Se publica después del commit (ADR-003)."""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Callable

from src.domain.events import (
    CapacidadJaulasAlcanzadaEvent,
    CitaAgendadaEvent,
    EmergenciaRegistradaEvent,
)

from .notificaciones import INotificacionService

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def subscribe(self, tipo_evento: type, handler: Callable) -> None:
        self._handlers[tipo_evento].append(handler)

    def publish(self, eventos: list) -> None:
        for evento in eventos:
            for handler in self._handlers.get(type(evento), []):
                try:
                    handler(evento)
                except Exception:  # un fallo de envío NO revierte la transacción de negocio
                    logger.exception("Falló el handler %s para %s", handler, type(evento).__name__)


class CitaAgendadaEventHandler:
    def __init__(self, notificaciones: INotificacionService):
        self._notificaciones = notificaciones

    def handle(self, evento: CitaAgendadaEvent) -> None:
        self._notificaciones.programar_recordatorio(evento)


def registrar_handlers(bus: EventBus, notificaciones: INotificacionService) -> None:
    bus.subscribe(CitaAgendadaEvent, CitaAgendadaEventHandler(notificaciones).handle)
    bus.subscribe(EmergenciaRegistradaEvent, notificaciones.alertar_veterinario)
    bus.subscribe(CapacidadJaulasAlcanzadaEvent, notificaciones.alertar_capacidad)
