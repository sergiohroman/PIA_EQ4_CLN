"""Adaptador de notificaciones (ADR-003).

WhatsAppNotificacionService deja los mensajes en un outbox (y en el log).
Para producción real basta sustituir `_enviar` por el proveedor (p. ej. Twilio/Meta Cloud API)
sin tocar dominio ni aplicación.
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, time, timedelta

from src.application.notificaciones import INotificacionService
from src.domain.events import (
    CapacidadJaulasAlcanzadaEvent,
    CitaAgendadaEvent,
    EmergenciaRegistradaEvent,
)

logger = logging.getLogger(__name__)


class WhatsAppNotificacionService(INotificacionService):
    def __init__(self) -> None:
        self.outbox: list[dict] = []
        self._lock = threading.Lock()

    def _registrar(self, tipo: str, destino: str | None, enviar_en: datetime | None, mensaje: str, **extra) -> None:
        mensaje_salida = {
            "tipo": tipo,
            "canal": "whatsapp",
            "destino": destino,
            "enviar_en": enviar_en.isoformat() if enviar_en else "inmediato",
            "mensaje": mensaje,
            "estado": "PROGRAMADO",
            **extra,
        }
        with self._lock:
            self.outbox.append(mensaje_salida)
        logger.info("Notificación %s -> %s", tipo, destino)

    def programar_recordatorio(self, evento: CitaAgendadaEvent) -> None:
        """US-09 (vacuna: 3 días antes a las 8:00) y US-10 (4 horas antes)."""
        if evento.tipo == "vacuna":
            fecha = (evento.inicio - timedelta(days=3)).date()
            self._registrar(
                "recordatorio_3_dias", evento.celular_propietario, datetime.combine(fecha, time(8, 0)),
                f"Recordatorio: su mascota tiene cita de vacunación el {evento.inicio:%d/%m/%Y a las %H:%M}.",
                cita_id=evento.cita_id,
            )
        self._registrar(
            "recordatorio_4_horas", evento.celular_propietario, evento.inicio - timedelta(hours=4),
            f"Recordatorio final: su cita es hoy a las {evento.inicio:%H:%M}.",
            cita_id=evento.cita_id,
        )

    def alertar_veterinario(self, evento: EmergenciaRegistradaEvent) -> None:
        self._registrar(
            "alerta_emergencia", evento.veterinario_id, None,
            f"EMERGENCIA: paciente {evento.mascota_id} requiere atención inmediata.",
            cita_id=evento.cita_id,
        )

    def alertar_capacidad(self, evento: CapacidadJaulasAlcanzadaEvent) -> None:
        self._registrar(
            "alerta_capacidad", "dashboard-administrativo", None,
            f"Hospitalización llena: {evento.ocupadas}/{evento.capacidad} jaulas ocupadas.",
        )
