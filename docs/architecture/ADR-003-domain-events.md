# ADR-003: Domain Events para recordatorios y alertas
**Estado:** Aceptada

**Contexto.** Los recordatorios por WhatsApp (N-003, US-09, US-10) y la alerta de emergencia (N-007, US-03) son efectos de hechos del negocio. La revisión SOLID (S) detectó que el servicio de citas coordinaba también el envío de mensajes.

**Alternativas.** Llamar a WhatsApp desde el Application Service (mezcla responsabilidades, ata a un proveedor); un proceso programado que revise la tabla de citas (no cubre alertas inmediatas).

**Decisión.** Los agregados registran eventos (`CitaAgendadaEvent`, `EmergenciaRegistradaEvent`, `CapacidadJaulasAlcanzadaEvent`, …). Tras el commit, el `EventBus` invoca handlers que usan el puerto `INotificacionService`, implementado por `WhatsAppNotificacionService` (outbox + log).

**Consecuencias.** (+) El dominio no conoce el canal; cambiar a SMS no afecta la Agenda. (−) El envío ocurre fuera de la transacción: un fallo no revierte la cita (el bus lo registra en el log). **Pendiente:** reintentos, persistencia del outbox y proveedor real.

**Trazabilidad.** N-003, N-007 · US-03, US-09, US-10 · `src/application/event_bus.py` · `tests/integration/test_api_citas.py`.
