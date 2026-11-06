# ADR-004: La regla de las 10 jaulas vive en el agregado Hospitalización
**Estado:** Aceptada

**Contexto.** La capacidad máxima (BR-002, N-006, US-12) es la regla más estricta; el ingreso puede iniciarse desde varios puntos del sistema.

**Alternativas.** Validar en el Application Service (otros puntos de entrada podrían saltarla); restricción solo en BD (error técnico, no del negocio).

**Decisión.** `Hospitalizacion.ingresar_paciente()` evalúa la Specification `HospitalizacionTieneCupo` y lanza `CapacidadMaximaJaulasAlcanzada`; la UoW hace rollback y la API responde 409 "Capacidad máxima de jaulas alcanzada". **Concurrencia (implementada en el PIA):** la fila `hospitalizacion` lleva `version` y `save()` hace comparar-y-actualizar (`UPDATE … WHERE version = :leida`, `SqlHospitalizacionRepository.save`); dos ingresos simultáneos sobre la misma versión producen `ConflictoDeConcurrencia` (409) en el segundo.

**Consecuencias.** (+) Regla en un solo lugar, probada sin infraestructura. (−) El cliente debe reintentar ante conflicto de versión.

**Trazabilidad.** BR-002, N-006 · US-12 · CU-04 · `tests/unit/test_hospitalizacion.py`, `tests/integration/test_persistencia.py`.
