# Documento de decisiones técnicas — VetCare 24

## 1. Arquitectura en capas
| Capa | Carpeta | Responsabilidad | Depende de |
|------|---------|-----------------|------------|
| Dominio | `src/domain` | Entidades, Value Objects, Aggregates, Specifications, State Machine, Domain Services/Events, puertos de repositorio | nada |
| Aplicación | `src/application` | Casos de uso (Application Services), DTOs, Commands/Queries, UoW (puerto), bus de eventos | dominio |
| Infraestructura | `src/infrastructure` | SQLAlchemy (ORM, repositorios, UoW), adaptador WhatsApp, configuración de BD | dominio, aplicación |
| API | `src/api` | Controllers REST, esquemas Pydantic, traducción de errores a HTTP, *composition root* | aplicación |

Regla de dependencia: las flechas apuntan hacia el dominio; `src/domain` no importa SQLAlchemy ni FastAPI.

## 2. Patrones aplicados y justificación
| Patrón | Dónde | Por qué (problema del negocio) |
|--------|-------|--------------------------------|
| Domain Model + Aggregates | `domain/expediente.py`, `agenda.py`, `hospitalizacion.py` | Invariantes críticas (10 jaulas, firma inmutable, celular único) |
| Value Object | `domain/value_objects.py` | `Celular`, `SignosVitales`, `RecetaMedica`, `FirmaDigital` inmutables y auto-validados |
| Domain Service | `domain/servicios_dominio.py` | Reglas que cruzan agregados (duplicidad de cliente, prioridad de emergencia) |
| Domain Events | `domain/events.py`, `application/event_bus.py` | Desacoplar recordatorios/alertas del flujo principal (ADR-003) |
| Specification | `domain/specification*.py` | Reglas componibles AND/OR/NOT (ADR-005) |
| State Machine | `domain/estados.py` | Ciclo de vida de cita y nota (ADR-006) |
| Strategy | `domain/servicios.py` | Duración por servicio; agregar estética sin tocar `Agenda` (OCP) |
| Repository + Unit of Work | `domain/repositories.py`, `infrastructure/` | Persistencia desacoplada y transacción por caso de uso (ADR-002) |
| CQRS básico | `application/commands.py`, `queries.py` | Separar escritura (reglas) de lectura (historial, ocupación, productividad) |
| DTO | `application/dtos.py` | Contratos entre API y casos de uso sin exponer entidades |
| Optimistic Locking | `infrastructure/repositories.py` (`UPDATE … WHERE version`) | Dos ingresos simultáneos no pueden exceder 10 jaulas (ADR-004) |

## 3. Evidencia de SOLID en el código
| Principio | Evidencia |
|-----------|-----------|
| **S** | `CitaApplicationService` solo coordina; el envío de mensajes lo hace `CitaAgendadaEventHandler` + `INotificacionService` |
| **O** | Nuevo servicio = nueva clase `IServicioCita` y `registrar_servicio()`; `Agenda` no cambia. Nueva regla = nueva `Specification` |
| **L** | Cualquier `IExpedienteRepository`/`IAgendaRepository` es sustituible (SQL o doble de prueba, ver `RepoFalso` en `tests/unit/test_expediente.py`) |
| **I** | Cuatro puertos de repositorio pequeños en lugar de un `ClinicaRepository` de 30 métodos |
| **D** | Los Application Services reciben `uow_factory` (abstracción); `Contenedor` (`src/api/container.py`) inyecta las implementaciones concretas |

## 4. Diferencias respecto al diseño de la Actividad 3
| Tema | Act. 3 | PIA | Motivo |
|------|--------|-----|--------|
| Persistencia | JPA | SQLAlchemy | Stack Python (ADR-007) |
| Specification / State Machine | no incluidas | incluidas | Requisito del PIA (ADR-005, ADR-006) |
| `signos vitales` | dentro de `Hospitalizacion` | igual; se persisten en `signos_vitales` y se cargan solo los posteriores al ingreso | Evitar mezclar estancias previas |
| Reportes | solo ocupación e historial | + productividad (US-14) y vacunas atrasadas (US-13, CSV/JSON) | Cobertura completa de N-008 |
| `Event Sourcing`, `Facturación`, `MedicamentoRecetado`, `TriageLevel` | aparecen en la bitácora de IA | **no implementados** | Fuera del diseño final; la bitácora debe reflejar solo lo adoptado |
| Cita: estados | Programada/EnAtencion/Completada/Cancelada | igual + mapeo al flujo del ZIP (BRD §12) | Trazabilidad con el paquete de pruebas |

## 5. Riesgos y deuda técnica conocida
- El *outbox* de notificaciones es en memoria: no hay reintentos ni proveedor real (ADR-003).
- Sin autenticación/roles: cualquier cliente de la API puede firmar con un `veterinario_id` válido.
- `create_all` en lugar de migraciones (Alembic).
- US-13: el BRD no define esquemas de vacunación por especie; se adoptó el criterio «cita de vacuna vencida y no aplicada». Un catálogo de refuerzos por especie sería evolución futura.
- La fusión de propietarios duplicados (dos expedientes de personas) no existe; solo se fusionan mascotas dentro de un expediente.
