# Documento de Requerimientos del Negocio (BRD) — VetCare 24

**Equipo 4 · Grupo 002 · Componentes de Lógica de Negocios (UANL-FIME) · Agosto–Diciembre 2026**
Integrantes: David Alejandro Vázquez Fernández (2110193), Sergio Humberto Román Puente (2099682), Edelyn Naomi Carrera García (2098207).

> Versión refinada para el PIA a partir de los artefactos de la Unidad 2 (Actividad 2) y la Unidad 3 (Actividad 3). Los cambios respecto a U2/U3 se listan en la sección 12.

## 1. Contexto
VetCare 24 es una clínica veterinaria 24/7 que ofrece consultas, vacunas, cirugías, estética, estudios y hospitalización. Cada propietario puede registrar varias mascotas y la clínica conserva la información clínica por animal. Hoy la operación depende de fichas en papel, lo que provoca expedientes duplicados, pérdida de historial y recordatorios manuales de vacunación.

## 2. Objetivos del negocio
| ID | Objetivo | Medida |
|----|----------|--------|
| OBJ-01 | Eliminar la duplicación de clientes y expedientes | CE-001 |
| OBJ-02 | Dar a los veterinarios acceso inmediato al historial y registrar notas/recetas sin papel | CE-002, CE-004 |
| OBJ-03 | Aumentar el regreso de pacientes a sus refuerzos de vacuna mediante recordatorios automáticos | CE-003 |
| OBJ-04 | Garantizar prioridad a emergencias y respetar la capacidad física de hospitalización | BR-002 |
| OBJ-05 | Dar a la administración indicadores de productividad y ocupación | N-008 |

## 3. Alcance
**Dentro del alcance (implementado en el PIA):** agenda y citas con duración por servicio, emergencias con prioridad, expedientes (propietarios, mascotas, notas, recetas, firma digital, fusión de duplicados), hospitalización con límite de 10 jaulas y signos vitales, recordatorios por Domain Events, reportes de productividad, ocupación y vacunas atrasadas (CSV/JSON), API REST documentada.
**Fuera del alcance de este incremento:** facturación y cobros, inventario de medicamentos, estética y estudios (el diseño los admite como nuevos `IServicioCita`), autenticación/roles de usuario, envío real a WhatsApp (se entrega un adaptador con *outbox*), y gráficos de productividad.

## 4. Stakeholders
| Stakeholder | Interés | Influencia | Interés |
|-------------|---------|-----------|---------|
| Propietario | Que su mascota reciba atención continua, sin duplicados ni fallas | Alta | Alta |
| Veterinario | Antecedentes clínicos rápidos; notas y recetas sin papel | Alta | Alta |
| Recepción | Agendar rápido, registrar llegada, evitar clientes repetidos | Media | Alta |
| Personal clínico | Registrar evolución y signos vitales de internados | Baja | Media |
| Administración | Reportes de productividad y ocupación | Media | Alta |

## 5. Operación actual (as-is)
La mascota se registra con nombre, especie, raza, sexo, fecha de nacimiento, peso y datos relevantes como alergias. Las citas dependen del servicio (una vacuna requiere menos tiempo que una consulta especializada). Al llegar se registra peso y motivo de consulta; el veterinario genera una nota clínica y puede indicar medicamentos, estudios, vacunas o seguimiento.

## 6. Necesidades
| Código | Necesidad |
|--------|-----------|
| N-001 | Organizar la agenda especificando el servicio (consulta, vacuna o cirugía) y mostrando espacios libres al momento |
| N-002 | Guardar la historia médica en un solo lugar digital, conectando varias mascotas a un mismo dueño con un dato único (celular) |
| N-003 | Avisos automáticos de vacunas por WhatsApp o mensaje 3 días antes y el mismo día de la cita |
| N-004 | Revisar si el cliente/paciente ya existe antes de registrarlo y permitir juntar archivos repetidos |
| N-005 | Guardar notas médicas, recetas y alergias digitalmente con la firma/aprobación del veterinario |
| N-006 | Controlar pacientes internados con signos vitales cada 4–6 h sin pasar el límite de 10 jaulas |
| N-007 | Avisar y dar prioridad a las urgencias médicas sobre las citas programadas |
| N-008 | Reportes de vacunas pendientes, consultas por doctor y ocupación de internado |

## 7. Reglas de negocio
| ID | Regla | Necesidad | Dónde vive en el código |
|----|-------|-----------|-------------------------|
| RN-01 | La duración de la cita depende del servicio: consulta 30 min, vacuna 15 min, cirugía 120 min (configurables; el BRD no las fija) | N-001 | `domain/servicios.py` (Strategy `IServicioCita`) |
| RN-02 | Un veterinario no puede tener dos citas activas traslapadas, salvo Emergencia | N-001, N-007 | `Agenda.agendar_cita` + Specification `CitaSinTraslape \| CitaEsEmergencia` |
| RN-03 | La emergencia tiene prioridad máxima: se coloca primero en la cola, marca para reprogramar las citas traslapadas y alerta al veterinario | N-007 | `AsignadorPrioridadEmergenciaService`, `Agenda.cola_espera` |
| RN-04 | El celular identifica al propietario y es único | N-002, N-004 | `ValidadorDuplicidadClienteService`, `CelularNoRegistrado`, índice único en BD |
| RN-05 | Todas las mascotas de una persona cuelgan del mismo expediente | N-002 | `ExpedienteClinico.registrar_mascota` |
| RN-06 | Dos mascotas duplicadas pueden fusionarse; el historial se consolida y el duplicado se elimina | N-004 | `ExpedienteClinico.fusionar_mascotas` |
| RN-07 | Una nota clínica firmada queda sellada con el ID del veterinario y no se modifica | N-005 | `NotaClinica.firmar/editar`, `NotaNoFirmada`, State Machine de nota |
| RN-08 | Nunca más de 10 jaulas ocupadas simultáneamente (BR-002) | N-006 | `Hospitalizacion.ingresar_paciente`, `HospitalizacionTieneCupo` |
| RN-09 | Los internados requieren toma de signos cada 4–6 h; se alerta a las 4 h | N-006 | `Hospitalizacion.signos_pendientes` |
| RN-10 | Recordatorio por WhatsApp 3 días antes (vacunas, 8:00) y 4 h antes de toda cita | N-003 | Evento `CitaAgendadaEvent` → `WhatsAppNotificacionService` |
| RN-11 | Estados de la cita: PROGRAMADA → EN_ATENCION → COMPLETADA; cancelación desde PROGRAMADA o EN_ATENCION; COMPLETADA y CANCELADA son terminales | N-001 | `domain/estados.py` (State Machine) |
| RN-12 | Importes en MXN con precisión decimal; `puede_procesarse` y `beneficio_referencia` (reglas del paquete de pruebas, ver §12) | — | `domain/operacion.py` |
| RN-13 | Vacuna atrasada: cita de vacuna vencida y no aplicada (`PROGRAMADA` o `CANCELADA`); se reporta con el contacto del dueño para seguimiento | N-008 | `domain/specifications.vacuna_atrasada` |

## 8. Requisitos funcionales
| ID | Requisito | Historias | Caso de uso |
|----|-----------|-----------|-------------|
| RF-01 | Agendar cita con asignación automática de tiempo y consultar espacios libres | US-01, US-02 | CU-01 |
| RF-02 | Registrar llegada como emergencia con prioridad y alerta | US-03 | CU-02 |
| RF-03 | Registrar propietarios con alerta de cliente existente; vincular mascotas; fusionar duplicados | US-04, US-05, US-06 | CU-03 |
| RF-04 | Guardar notas, recetas, peso y alergias; firmar y sellar | US-07, US-08 | CU-03 |
| RF-05 | Enviar recordatorios 3 días antes y 4 horas antes | US-09, US-10 | efecto de CU-01 |
| RF-06 | Internar pacientes respetando el límite de 10 jaulas; registrar y vigilar signos vitales | US-11, US-12 | CU-04 |
| RF-07 | Reportes: ocupación, productividad y vacunas atrasadas (exportables) | US-13, US-14, US-15 | Queries |

## 9. Requisitos no funcionales
| ID | Requisito |
|----|-----------|
| RNF-01 | Protección de datos personales de los propietarios (BR-001): sin datos reales en el repositorio; configuración y secretos fuera del código (`.env`) |
| RNF-02 | Abrir el historial completo de una mascota en < 10 s (CE-002): consulta por índices (`mascotas.id`, `notas_clinicas.mascota_id`) |
| RNF-03 | Reproducibilidad: Docker Compose para DB + App + Tests; configuración 12-Factor |
| RNF-04 | Calidad: pruebas unitarias e integración con cobertura ≥ 80 % y CI en cada *push* |
| RNF-05 | Contrato API documentado con OpenAPI/Swagger |
| RNF-06 | Integridad ante concurrencia en hospitalización (bloqueo optimista, ADR-004) |

## 10. Restricciones y supuestos
| Código | Tipo | Descripción |
|--------|------|-------------|
| BR-001 | Restricción | Cumplir la ley de protección de datos personales |
| BR-002 | Restricción | Máximo 10 mascotas internadas simultáneamente (límite físico) |
| BR-003 | Restricción | Entrega y puesta en marcha en máximo 10 semanas |
| SU-001 | Supuesto | La clínica cuenta con dispositivos con internet estable en recepción y consultorios *(antes BR-004)* |
| SU-002 | Supuesto | Los propietarios tienen dispositivos móviles que reciben SMS/WhatsApp *(antes BR-005)* |

## 11. Criterios de éxito
| Código | Criterio | Meta |
|--------|----------|------|
| CE-001 | Cero duplicados | Ningún expediente repetido en los primeros 3 meses |
| CE-002 | Rapidez en consulta | Historial completo en < 10 segundos |
| CE-003 | Regreso para vacunas | 8 de cada 10 pacientes regresan a su refuerzo con recordatorios, en 6 meses |
| CE-004 | Cero papeles | Sin fichas ni notas impresas al terminar el primer mes |

## 12. Cambios respecto a U2/U3 (refinamiento para el PIA)
1. **Supuestos renombrados** (BR-004/005 → SU-001/002) para no confundirlos con restricciones.
2. **Duración y estados explícitos**: se fijan duraciones por defecto (RN-01) y el ciclo de vida de la cita (RN-11), que U2/U3 dejaban implícitos.
3. **Estados del paquete de pruebas**: el ZIP propone SOLICITADA → CONFIRMADA → REALIZADA → CANCELADA. El equipo conserva su modelo (PROGRAMADA, EN_ATENCION, COMPLETADA, CANCELADA) y documenta el mapeo: SOLICITADA = PROGRAMADA, CONFIRMADA (`aprobar`) = EN_ATENCION, REALIZADA (`completar`) = COMPLETADA, CANCELADA = CANCELADA.
4. **Reglas del paquete de pruebas** (`puede_procesarse`, `beneficio_referencia`, importes en MXN) se implementan como *adaptador de evaluación* sobre un modelo `OperacionVeterinaria` separado, sin reemplazar las reglas propias del BRD (ADR-005).
5. **Repositorios**: se confirma un repositorio por Aggregate Root (hallazgos 1 y 2 de la Etapa 9 de la Act. 3).
6. **Stack**: Python + FastAPI + SQLAlchemy (ADR-007) en lugar de JPA/C# mencionados en borradores de U3.
7. **Bitácora de IA**: corregida para reflejar únicamente decisiones presentes en el diseño final.
