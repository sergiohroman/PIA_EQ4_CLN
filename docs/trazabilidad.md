# Matriz de trazabilidad: BRD → historia → regla → componente → endpoint → prueba

Estado: ✅ implementada y probada · 🟡 parcial · ⬜ no implementada.
Rutas de prueba relativas a `tests/`; `unit/` = pruebas del dominio, `integration/` = API + BD.

| Necesidad | Historia | Caso de uso | Regla | Componentes (src/) | Endpoint | Pruebas | Estado |
|-----------|----------|-------------|-------|--------------------|----------|---------|--------|
| N-001 | US-01 | CU-01 | RN-01, RN-02 | `domain/agenda.py`, `domain/servicios.py`, `application/services.CitaApplicationService` | `POST /citas` | `unit/test_agenda.py::test_us01_*`, `::test_no_permite_traslape_*`; `integration/test_api_citas.py::test_us01_*`, `::test_traslape_*` | ✅ |
| N-001 | US-02 | CU-01 | RN-01 | `Agenda.espacios_libres` | `GET /citas/espacios-libres` | `unit/test_agenda.py::test_us02_*`; `integration/test_api_citas.py::test_us02_*` | ✅ |
| N-007 | US-03 | CU-02 | RN-03 | `AsignadorPrioridadEmergenciaService`, `EmergenciaRegistradaEvent` | `POST /emergencias`, `GET /citas/cola` | `unit/test_agenda.py::test_us03_*`; `integration/test_api_citas.py::test_us03_*` | ✅ |
| N-004 | US-04 | CU-03 | RN-04 | `ValidadorDuplicidadClienteService`, `CelularNoRegistrado`, índice único `propietarios.celular` | `POST /expedientes` | `unit/test_expediente.py::test_us04_*`; `integration/test_api_expedientes.py::test_us04_*` | ✅ |
| N-004 | US-05 | CU-03 | RN-06 | `ExpedienteClinico.fusionar_mascotas` | `POST /expedientes/{celular}/mascotas/fusion` | `unit/test_expediente.py::test_us05_*`; `integration/test_api_expedientes.py::test_us05_*` | ✅ |
| N-002 | US-06 | CU-03 | RN-05 | `ExpedienteClinico.registrar_mascota` | `POST /expedientes/{celular}/mascotas` | `unit/test_expediente.py::test_us06_*`; `integration/test_api_expedientes.py::test_us06_*` | ✅ |
| N-005 | US-07 | CU-03 | RN-07 | `ExpedienteClinico.registrar_nota`, `RecetaMedica` | `POST /mascotas/{id}/notas`, `POST /expedientes/{celular}/mascotas-con-nota` | `unit/test_expediente.py::test_us07_*`; `integration/test_api_expedientes.py::test_us07_*`, `::test_cu03_*` | ✅ |
| N-005 | US-08 | CU-03 | RN-07 | `NotaClinica.firmar/editar`, `FirmaDigital`, `MAQUINA_NOTA`, `NotaNoFirmada` | `POST /notas/{id}/firma`, `PUT /notas/{id}` | `unit/test_expediente.py::test_us08_*`; `integration/test_api_expedientes.py::test_us08_*` | ✅ |
| N-003 | US-09 | CU-01 (efecto) | RN-10 | `CitaAgendadaEvent`, `CitaAgendadaEventHandler`, `WhatsAppNotificacionService` | `GET /notificaciones` | `integration/test_api_citas.py::test_us09_us10_*`, `::test_consulta_no_genera_*` | 🟡 programa mensajes (outbox); no hay proveedor real ni *scheduler* de las 8:00 |
| N-003 | US-10 | CU-01 (efecto) | RN-10 | ídem | `GET /notificaciones` | `integration/test_api_citas.py::test_us09_us10_*` | 🟡 igual que US-09 |
| N-006 | US-11 | CU-04 | RN-09 | `Hospitalizacion.registrar_signos/signos_pendientes`, `SignosVitales` | `POST /hospitalizacion/signos-vitales`, `GET /hospitalizacion/signos-pendientes` | `unit/test_hospitalizacion.py::test_us11_*`; `integration/test_api_hospitalizacion.py::test_us11_*` | ✅ (alerta por consulta, sin *push*) |
| N-006, BR-002 | US-12 | CU-04 | RN-08 | `Hospitalizacion.ingresar_paciente`, `HospitalizacionTieneCupo`, `CapacidadMaximaJaulasAlcanzada`, `UPDATE … WHERE version` (bloqueo optimista) | `POST /hospitalizacion/ingresos` | `unit/test_hospitalizacion.py::test_us12_*`; `integration/test_api_hospitalizacion.py::test_us12_*`; `integration/test_persistencia.py::test_dos_ingresos_simultaneos_*` | ✅ |
| N-008 | US-13 | Query | RN-13 | `domain/specifications.vacuna_atrasada`, `ConsultarVacunasPendientesHandler` | `GET /reportes/vacunas-pendientes` (`?formato=csv`) | `unit/test_specification.py::test_us13_*`; `integration/test_api_reportes.py::test_us13_*` | ✅ |
| N-008 | US-14 | Query | — | `ConsultarProductividadHandler` | `GET /reportes/productividad` | `integration/test_api_reportes.py::test_us14_*` | 🟡 sin gráfico |
| N-008 | US-15 | Query | RN-08 | `ConsultarOcupacionJaulasHandler`, `Hospitalizacion.ocupacion` | `GET /hospitalizacion/ocupacion` | `unit/test_hospitalizacion.py::test_ocupacion_us15`; `integration/test_api_hospitalizacion.py::test_us15_*` | ✅ |
| N-002 / CE-002 | — | Query | — | `ConsultarHistorialMascotaHandler` | `GET /mascotas/{id}/historial` | `integration/test_api_expedientes.py::test_us05_*` (consulta historial) | ✅ |
| (paquete de pruebas) | — | — | RN-11, RN-12 | `MAQUINA_CITA`, `domain/operacion.py`, `application/evaluacion_reglas.py` | `POST /citas/{id}/transiciones`, `POST /reglas/operaciones/evaluar` | `unit/test_state_machine.py`, `unit/test_reglas_operacion.py`, `integration/test_api_reportes.py::test_evaluar_*` | ✅ evidencia en `docs/evidencias/` |

## BPMN → código
| Carril / tarea BPMN | Implementación |
|---------------------|----------------|
| Recepcionista: registrar cita, seleccionar servicio, ver espacios libres | `POST /citas`, `GET /citas/espacios-libres` |
| Recepcionista: buscar cliente por celular / ¿existe? / registrar / vincular / fusionar | `GET /expedientes/{celular}`, `POST /expedientes`, `.../mascotas`, `.../fusion` |
| Recepcionista: activar «Emergencia» | `POST /emergencias` |
| Veterinario: notas, recetas, «Guardar y Firmar» | `POST /mascotas/{id}/notas` (`firmar=true`), `POST /notas/{id}/firma` |
| Veterinario: internar paciente / signos vitales | `POST /hospitalizacion/ingresos`, `POST /hospitalizacion/signos-vitales` |
| Administrador: reportes y ocupación | `GET /reportes/productividad`, `GET /hospitalizacion/ocupacion` |
| Sistema: bloquear tiempo, validar celular, alertar, sellar, recordatorios, validar 10 jaulas | Agenda, `ValidadorDuplicidadClienteService`, Domain Events, `NotaClinica.firmar`, `Hospitalizacion` |
