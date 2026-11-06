# Diagramas UML

## Diagramas de diseño (Actividad 3)
Diseño original previo a la implementación, en [`diagrams/`](diagrams/):

| Archivo | Contenido |
|---------|-----------|
| `mapa_dominio.png` | Mapa de dominio: 3 agregados, Value Objects, Domain Services y Domain Events |
| `clases_act3.png` | Clases por capas (Dominio / Aplicación / Infraestructura) |
| `secuencia_cu01_agendar_cita.png` / `.mmd` | CU-01, flujo principal (N-001) |
| `secuencia_cu04_ingreso_hospitalizacion.png` / `.mmd` | CU-04, flujo con rechazo y rollback (BR-002) |

> **Evolución diseño → código.** El diseño de la Act. 3 hablaba de repositorios «JPA»; la implementación usa **SQLAlchemy** (`SqlXRepository`) bajo los mismos puertos (`IXRepository`). Además, el PIA añadió la State Machine (`MAQUINA_CITA`, `MAQUINA_NOTA`), Specifications compuestas, versionado optimista en `Hospitalizacion` (ADR-004) y `IVeterinarioRepository`. Los diagramas Mermaid de abajo reflejan **el código final**.
Los siguientes diagramas (Mermaid, se renderizan en GitHub) reflejan **el código implementado**.

## Clases (dominio + puertos)
```mermaid
classDiagram
    class AggregateRoot { +pull_events() }
    class ExpedienteClinico { +registrar_mascota() +fusionar_mascotas() +registrar_nota() +firmar_nota() +modificar_nota() +historial() }
    class Propietario { id nombre celular }
    class Mascota { id nombre especie peso alergias }
    class NotaClinica { id estado firma receta +firmar() +editar() }
    class Agenda { fecha +agendar_cita() +espacios_libres() +cola_espera() +transicionar_cita() }
    class Cita { id tipo inicio fin estado es_emergencia +transicionar() }
    class Hospitalizacion { capacidad=10 version +ingresar_paciente() +dar_alta() +registrar_signos() +signos_pendientes() }
    class Jaula { numero mascota_id }
    class StateMachine { +siguiente() +acciones_permitidas() }
    class Specification { <<abstract>> +is_satisfied_by() }
    class IServicioCita { <<interface>> +duracion() }
    class ValidadorDuplicidadClienteService
    class AsignadorPrioridadEmergenciaService
    class IExpedienteRepository { <<interface>> }
    class IAgendaRepository { <<interface>> }
    class IHospitalizacionRepository { <<interface>> }
    AggregateRoot <|-- ExpedienteClinico
    AggregateRoot <|-- Agenda
    AggregateRoot <|-- Hospitalizacion
    ExpedienteClinico *-- Propietario
    ExpedienteClinico *-- "1..*" Mascota
    ExpedienteClinico *-- "*" NotaClinica
    Agenda *-- "*" Cita
    Hospitalizacion *-- "10" Jaula
    Cita ..> StateMachine : MAQUINA_CITA
    NotaClinica ..> StateMachine : MAQUINA_NOTA
    Agenda ..> IServicioCita
    Agenda ..> Specification
    Hospitalizacion ..> Specification
    ValidadorDuplicidadClienteService ..> IExpedienteRepository
    AsignadorPrioridadEmergenciaService ..> Agenda
    IExpedienteRepository ..> ExpedienteClinico
    IAgendaRepository ..> Agenda
    IHospitalizacionRepository ..> Hospitalizacion
```

## Capas y dependencias
```mermaid
flowchart LR
    API[src/api<br/>routers + schemas] --> APP[src/application<br/>services, queries, commands]
    APP --> DOM[src/domain<br/>aggregates, specs, state machine]
    INF[src/infrastructure<br/>SQLAlchemy, WhatsApp] --> APP
    INF --> DOM
```

## Secuencia CU-04: ingreso a hospitalización con rechazo
```mermaid
sequenceDiagram
    actor Vet as Veterinario
    participant API as POST /hospitalizacion/ingresos
    participant S as HospitalizacionApplicationService
    participant U as IUnitOfWork
    participant H as Hospitalizacion
    Vet->>API: IngresoIn
    API->>S: ingresar_paciente(dto)
    S->>U: __enter__ (inicia transacción)
    S->>U: hospitalizacion.obtener_actual()
    S->>H: ingresar_paciente(mascota, vet, motivo)
    alt ocupadas < 10
        H-->>S: Jaula + PacienteInternadoEvent
        S->>U: save() y commit()
        U-->>S: eventos publicados (alerta si llega a 10)
        S-->>API: EstadoJaulasDto
        API-->>Vet: 201
    else ocupadas = 10
        H-->>S: CapacidadMaximaJaulasAlcanzada
        S->>U: __exit__ con excepción → rollback
        API-->>Vet: 409 "Capacidad máxima de jaulas alcanzada"
    end
```

## Secuencia CU-01: agendar cita
```mermaid
sequenceDiagram
    actor R as Recepción
    participant S as CitaApplicationService
    participant U as IUnitOfWork
    participant A as Agenda
    participant B as EventBus
    participant N as INotificacionService
    R->>S: agendar_cita(SolicitudCitaDto)
    S->>U: get_by_mascota_id / get_by_fecha
    S->>A: agendar_cita(tipo, vet, inicio)
    A->>A: duración (IServicioCita) + CitaSinTraslape | CitaEsEmergencia
    A-->>S: Cita (+ CitaAgendadaEvent)
    S->>U: save(agenda) y commit()
    U->>B: publish(eventos) tras el commit
    B->>N: programar_recordatorio(evento)
    S-->>R: RespuestaCitaDto (cita + espacios libres)
```
