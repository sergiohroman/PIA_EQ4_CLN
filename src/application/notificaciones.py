"""Puerto de notificaciones (ADR-003): el dominio no conoce el canal (WhatsApp/SMS)."""
from abc import ABC, abstractmethod

from src.domain.events import (
    CapacidadJaulasAlcanzadaEvent,
    CitaAgendadaEvent,
    EmergenciaRegistradaEvent,
)


class INotificacionService(ABC):
    @abstractmethod
    def programar_recordatorio(self, evento: CitaAgendadaEvent) -> None: ...

    @abstractmethod
    def alertar_veterinario(self, evento: EmergenciaRegistradaEvent) -> None: ...

    @abstractmethod
    def alertar_capacidad(self, evento: CapacidadJaulasAlcanzadaEvent) -> None: ...
