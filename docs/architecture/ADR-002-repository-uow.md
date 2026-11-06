# ADR-002: Un Repository por Aggregate Root y Unit of Work por caso de uso
**Estado:** Aceptada (actualizada en el PIA: SQLAlchemy en lugar de JPA)

**Contexto.** Los Application Services no deben depender de SQL ni del ORM, y operaciones como internar un paciente o guardar una nota firmada deben completarse juntas o no aplicarse. La revisión SOLID detectó un repositorio con más de 30 métodos (ISP) y acceso directo a PostgreSQL desde un servicio (DIP).

**Alternativas.** `ClinicaRepository` general (viola ISP); un repositorio por tabla (expone el interior del agregado); acceso a BD desde el servicio (acopla a infraestructura).

**Decisión.** Puertos `IExpedienteRepository`, `IAgendaRepository`, `IHospitalizacionRepository` e `IVeterinarioRepository` en `src/domain/repositories.py`; implementaciones SQLAlchemy en `src/infrastructure/repositories.py`. `IUnitOfWork` abre la transacción en el método del Application Service y hace *commit* o *rollback*; los Domain Events se publican **después** del commit.

**Consecuencias.** (+) Dominio sin SQL; repositorios sustituibles (LSP). (−) Más interfaces y mapeo dominio ↔ ORM.

**Trazabilidad.** N-001, N-004, N-006, BR-002 · `src/application/unit_of_work.py`, `src/infrastructure/unit_of_work.py` · `tests/integration/test_persistencia.py`.
