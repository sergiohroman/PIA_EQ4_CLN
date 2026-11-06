# Historias de usuario y criterios de aceptación (Gherkin) — VetCare 24

Cada historia indica necesidad (BRD), caso de uso, estado de implementación y pruebas que la verifican (ver `docs/trazabilidad.md`).
Los escenarios 1 provienen de la Actividad 2; los escenarios "alterno/negativo" se añadieron en el PIA.

## Módulo Agenda y Citas

### US-01 · N-001 · CU-01
**Como** recepción, **quiero** agendar citas seleccionando el tipo de servicio (consulta, vacuna o cirugía), **para que** el sistema asigne automáticamente el tiempo adecuado.
```gherkin
Scenario: Bloquear el tiempo según el servicio
  Given que el recepcionista está en la pantalla de nueva cita
  When selecciona un tipo de servicio (ej. vacuna)
  Then el sistema bloquea en el calendario el tiempo predeterminado para ese servicio

Scenario: Rechazar un horario traslapado (alterno)
  Given que el veterinario ya tiene una consulta de 09:00 a 09:30
  When recepción intenta agendar una vacuna a las 09:15 con el mismo veterinario
  Then el sistema responde 409 "El veterinario ya tiene una cita en ese horario"
```
### US-02 · N-001 · CU-01
**Como** recepción, **quiero** visualizar los espacios libres en tiempo real, **para** ofrecer horarios disponibles rápidamente.
```gherkin
Scenario: Mostrar bloques libres
  Given que un cliente solicita una cita
  When el recepcionista abre el calendario del día
  Then el sistema resalta los bloques de tiempo libres

Scenario: Un horario ocupado deja de ofrecerse (alterno)
  Given que existe una cita de 08:00 a 08:30 del veterinario V1
  When se consultan los espacios libres de V1 para una consulta
  Then ningún bloque ofrecido inicia entre 08:00 y 08:29
```
### US-03 · N-007 · CU-02
**Como** recepción, **quiero** registrar la llegada de un paciente como "emergencia", **para** darle prioridad máxima.
```gherkin
Scenario: Emergencia al frente de la cola
  Given que llega un paciente grave sin cita
  When el recepcionista activa la opción "Emergencia"
  Then el paciente se coloca al principio de la cola de espera
  And el sistema alerta al veterinario

Scenario: Emergencia sobre una cita regular (alterno)
  Given una consulta programada de 10:00 a 10:30
  When llega una emergencia a las 10:10 para el mismo veterinario
  Then la emergencia se registra pese al traslape
  And la cita regular se marca "requiere reprogramación"
```

## Módulo Expedientes Clínicos y Pacientes

### US-04 · N-004 · CU-03
**Como** recepción, **quiero** que el sistema me alerte si el celular ya existe, **para** evitar clientes repetidos.
```gherkin
Scenario: Alertar cliente existente
  Given que el recepcionista ingresa los datos de un nuevo cliente
  When introduce un celular que ya está en la base de datos
  Then el sistema muestra "Cliente existente" y sugiere abrir el perfil actual (409)

Scenario: Celular con formato distinto pero mismo número (alterno)
  Given un propietario registrado con 8112345678
  When se registra otro con "81-1234-5678"
  Then el sistema lo detecta como duplicado

Scenario: Celular inválido (negativo)
  When se registra un propietario con celular "abc"
  Then el sistema responde 422
```
### US-05 · N-004 · CU-03
**Como** recepción, **quiero** fusionar archivos repetidos, **para** unificar el historial de una mascota duplicada.
```gherkin
Scenario: Fusionar duplicados
  Given que existen dos expedientes para la misma mascota
  When el recepcionista selecciona ambos y hace clic en "Fusionar"
  Then el sistema consolida el historial en un solo archivo y elimina el duplicado

Scenario: Origen y destino iguales (negativo)
  When se intenta fusionar una mascota consigo misma
  Then el sistema responde 422
```
### US-06 · N-002 · CU-03
**Como** propietario, **quiero** tener todas mis mascotas bajo mi mismo número de contacto, **para** que la clínica agrupe mi información.
```gherkin
Scenario: Agregar mascota al propietario
  Given que un cliente ya registrado lleva una mascota nueva
  When el recepcionista busca al cliente por su celular
  Then puede agregar un nuevo perfil de mascota vinculado a ese mismo dueño

Scenario: Propietario inexistente (negativo)
  When se busca un celular no registrado
  Then el sistema responde 404
```
### US-07 · N-005 · CU-03
**Como** veterinario, **quiero** registrar notas, peso, alergias y recetas, **para** eliminar el papel.
```gherkin
Scenario: Guardar nota
  Given que el veterinario está en una consulta activa
  When finaliza la revisión
  Then el sistema guarda notas y receta y actualiza peso y alergias en el perfil de la mascota

Scenario: Veterinario inexistente (negativo)
  When se guarda una nota con un veterinario que no existe
  Then el sistema responde 404 y no se guarda nada
```
### US-08 · N-005 · CU-03
**Como** veterinario, **quiero** aprobar notas y recetas con mi firma digital, **para** validar legalmente el tratamiento.
```gherkin
Scenario: Guardar y firmar
  Given que el veterinario redacta una receta
  When hace clic en "Guardar y Firmar"
  Then el sistema sella el documento con su ID de usuario
  And no permite modificaciones posteriores

Scenario: Modificar una nota firmada (negativo)
  Given una nota firmada
  When se intenta editarla
  Then el sistema responde 409 "La nota clínica ya fue firmada y no puede modificarse"
```

## Módulo Recordatorios de Vacunación

### US-09 · N-003
**Como** propietario, **quiero** un aviso por WhatsApp 3 días antes de mi cita de vacunación.
```gherkin
Scenario: Recordatorio a 3 días
  Given una cita de vacunación el 20/11 a las 10:00
  When se agenda la cita
  Then se programa un mensaje al celular del dueño para el 17/11 a las 08:00

Scenario: Una consulta no genera aviso de 3 días (alterno)
  Given una cita de consulta
  When se agenda
  Then solo se programa el aviso de 4 horas
```
### US-10 · N-003
**Como** recepción, **quiero** un segundo aviso el mismo día de la cita, **para** asegurar la asistencia.
```gherkin
Scenario: Recordatorio final
  Given una cita a las 10:00
  When se agenda
  Then se programa un mensaje para las 06:00 del mismo día (4 horas antes)
```

## Módulo Hospitalización

### US-11 · N-006 · CU-04
**Como** personal clínico, **quiero** registrar signos vitales cada 4 a 6 horas, **para** monitorear la evolución.
```gherkin
Scenario: Alerta de toma pendiente
  Given un paciente internado
  When pasan 4 horas desde la última toma (o desde el ingreso)
  Then el sistema lista al paciente como "signos pendientes"

Scenario: Signos fuera de rango (negativo)
  When se registra temperatura 50 °C
  Then el sistema responde 422
```
### US-12 · N-006, BR-002 · CU-04
**Como** veterinario, **quiero** que el sistema impida ingresar más pacientes si el área está llena, **para** no sobrepasar las 10 jaulas.
```gherkin
Scenario: Hospitalización llena
  Given que hay 10 mascotas con estatus "Internado"
  When el veterinario intenta internar a un nuevo paciente
  Then el sistema muestra "Capacidad máxima de jaulas alcanzada" (409)
  And la ocupación permanece en 10 (rollback)

Scenario: Alta libera cupo (alterno)
  Given 10 jaulas ocupadas
  When se da de alta a un paciente
  Then se puede internar un nuevo paciente
```

## Módulo Reportes e Indicadores

### US-13 · N-008
**Como** administración, **quiero** un reporte de pacientes con vacunas atrasadas, **para** campañas de seguimiento.
```gherkin
Scenario: Exportar vacunas pendientes
  Given que el administrador accede a reportes
  When selecciona "Vacunas pendientes" y un rango de fechas
  Then el sistema exporta mascotas y contactos de sus dueños

Scenario: Una vacuna ya aplicada no aparece como pendiente
  Given una cita de vacuna COMPLETADA dentro del rango
  When se genera el reporte de vacunas pendientes
  Then la mascota no aparece en la lista
```
*Criterio adoptado (el BRD no define esquemas de vacunación por especie):* **vacuna atrasada** = cita de tipo vacuna cuya hora ya pasó y que no se aplicó (estado `PROGRAMADA` o `CANCELADA`). Se modela como Specification compuesta `vacuna_atrasada` (`CitaEsVacuna & CitaVencida & CitaConEstado`). Exporta JSON o CSV (`?formato=csv`).

### US-14 · N-008
**Como** administración, **quiero** el número de atenciones por veterinario, **para** evaluar rendimiento.
```gherkin
Scenario: Productividad por doctor
  Given que terminó el mes
  When el gerente solicita el reporte de productividad
  Then el sistema desglosa consultas, cirugías y vacunas completadas por doctor
```
*Implementado como tabla JSON (sin gráfico).*

### US-15 · N-008
**Como** administración, **quiero** ver qué tan llena está el área de internado, **para** analizar la capacidad.
```gherkin
Scenario: Ocupación en tiempo real
  Given que el administrador revisa el dashboard
  When consulta la sección de ocupación
  Then el sistema muestra el porcentaje de jaulas utilizadas (ej. 8/10 = 80 %)
```
