# Guion de defensa: preguntas técnicas probables

**1. ¿Por qué Domain Model y no Transaction Script?** Las reglas (10 jaulas, celular único, nota firmada inmutable, prioridad de emergencia) son invariantes que deben cumplirse siempre; en el agregado se prueban sin base de datos (ADR-001).

**2. ¿Dónde vive la regla de las 10 jaulas y cómo se protege de concurrencia?** En `Hospitalizacion.ingresar_paciente`, que lanza `CapacidadMaximaJaulasAlcanzada` (API: 409). La BD protege con bloqueo optimista (`UPDATE ... WHERE version`) y el Unit of Work hace rollback: la ocupación sigue en 10/10 (ADR-004).

**3. ¿Qué es Specification y dónde la usan?** Reglas como objetos combinables con AND/OR/NOT: `CitaSinTraslape | CitaEsEmergencia` (agenda), `CitaEsVacuna & CitaVencida & CitaConEstado(...)` (US-13) y las reglas `puede_procesarse` / `beneficio_referencia` del paquete (ADR-005).

**4. ¿Cómo funciona la State Machine?** `MAQUINA_CITA` es una tabla de transiciones permitidas: PROGRAMADA → EN_ATENCION (aprobar) → COMPLETADA (completar); cancelar desde PROGRAMADA o EN_ATENCION. Una transición fuera de la tabla lanza `TransicionInvalida` (409). `MAQUINA_NOTA`: BORRADOR → FIRMADA (ADR-006).

**5. Sus estados no son los del paquete del docente.** El BRD documenta el mapeo: SOLICITADA = PROGRAMADA, CONFIRMADA = EN_ATENCION, REALIZADA = COMPLETADA, CANCELADA = CANCELADA. Los 120 casos y 20 transiciones se ejecutaron con `scripts/evaluar_casos_vetcare.py` (evidencia en `docs/evidencias/`).

**6. ¿Qué cambió respecto a la Actividad 3?** JPA pasó a SQLAlchemy sin tocar el dominio (gracias a Repository + UoW); se agregaron Specification y State Machine; se descartaron Event Sourcing, Facturación y C# por alcance (`decisiones_tecnicas.md` §4, ADR-007).

**7. ¿Cómo demuestran SOLID?** S: el servicio coordina y un handler envía mensajes. O: nuevo servicio = nueva clase `IServicioCita`. L: cualquier repositorio es sustituible (doble de prueba). I: un puerto pequeño por agregado. D: los servicios reciben `uow_factory`, el contenedor inyecta lo concreto.

**8. ¿Cuándo se publican los Domain Events?** Después del commit, para no avisar de algo que se revirtió (ADR-003). El envío a WhatsApp es un *outbox* en memoria (alcance parcial declarado en US-09/US-10).

**9. ¿Cómo se rastrea una regla?** `docs/trazabilidad.md`: necesidad → historia → caso de uso → componente → endpoint → prueba (ej. N-006 → US-12 → CU-04 → `ingresar_paciente` → `POST /hospitalizacion/ingresos`).

**10. Límites conocidos.** Sin autenticación ni roles, sin migraciones (usa `create_all`), recordatorios sin proveedor real ni scheduler, productividad sin gráfico.

**Demo (5 min):** seguir el guion del README; cerrar mostrando `docs/trazabilidad.md` y el CI en verde.
