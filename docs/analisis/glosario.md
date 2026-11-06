# Glosario de dominio — VetCare 24 (lenguaje ubicuo)

| Término | Definición | En el código |
|---------|-----------|--------------|
| Administración | Rol que consulta métricas, reportes de productividad y ocupación | `ConsultarProductividadHandler`, `ConsultarOcupacionJaulasHandler` |
| Agenda | Organiza las citas de un día, calcula espacios libres y evita traslapes | `Agenda` (Aggregate Root) |
| Alergia | Reacción adversa del paciente registrada en el perfil | `Mascota.alergias` |
| Capacidad máxima | Límite físico de 10 jaulas ocupadas simultáneamente | `CAPACIDAD_MAXIMA`, `Hospitalizacion` |
| Cita | Espacio reservado en la agenda; su duración depende del servicio | `Cita` |
| Cliente existente | Propietario cuyo celular ya está registrado | `ClienteExistenteException` |
| Consulta | Servicio médico donde el veterinario evalúa al paciente | `TipoServicio.CONSULTA` |
| Emergencia | Situación crítica que interrumpe la cola normal con prioridad máxima | `Cita.es_emergencia`, `EmergenciaRegistradaEvent` |
| Expediente clínico | Registro digital centralizado: propietario, mascotas y notas | `ExpedienteClinico` (Aggregate Root) |
| Expedientes duplicados | Archivos redundantes de una misma mascota | `fusionar_mascotas` |
| Firma digital | Sello del veterinario que impide modificar una nota | `FirmaDigital` |
| Fusión de archivos | Unificar historiales repetidos en uno consolidado | `ExpedienteClinico.fusionar_mascotas` |
| Hospitalización (internado) | Área con observación continua del paciente | `Hospitalizacion` (Aggregate Root) |
| Jaula | Espacio físico de internado (estado Disponible/Ocupada) | `Jaula` |
| Mascota (paciente) | Animal atendido: nombre, especie, raza, sexo, peso, nacimiento | `Mascota` |
| Motivo de consulta | Razón principal de la visita | `IngresoInternadoDto.motivo_ingreso` / nota |
| Nota clínica | Documento del veterinario con diagnóstico, evolución e indicaciones | `NotaClinica` |
| Personal clínico | Quien toma signos vitales en hospitalización | actor |
| Propietario | Persona responsable de las mascotas, identificada por su celular | `Propietario`, `Celular` |
| Recepción | Actor que agenda, registra llegadas y verifica clientes | actor |
| Receta médica | Medicamentos, dosis e indicaciones prescritos | `RecetaMedica` |
| Recordatorio de vacunación | Aviso por WhatsApp 3 días antes y 4 h antes | `WhatsAppNotificacionService` |
| Refuerzo | Dosis adicional periódica de una vacuna | `vacuna_atrasada` (US-13) |
| Signos vitales | Temperatura, frecuencia cardiaca y respiratoria, cada 4–6 h | `SignosVitales` |
| Sistema / Backend | Actor automatizado: alertas, validaciones, recordatorios, reportes | capa Application/Infrastructure |
| Veterinario | Profesional que atiende, redacta notas, prescribe y firma | `Veterinario` |
| Operación (paquete de pruebas) | Registro del ZIP con importes MXN, usado para evaluar Specifications | `OperacionVeterinaria` |
| Vacuna atrasada | Cita de vacuna cuya hora ya pasó y que no se aplicó (PROGRAMADA o CANCELADA); base del reporte de seguimiento | `vacuna_atrasada` (Specification), `ConsultarVacunasPendientesHandler` |
