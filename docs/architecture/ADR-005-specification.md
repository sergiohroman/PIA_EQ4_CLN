# ADR-005: Patrón Specification con composición AND/OR/NOT
**Estado:** Aceptada (nueva en el PIA)

**Contexto.** Varias reglas son predicados que se combinan y deben poder leerse en lenguaje del negocio: "sin traslape **o** emergencia" (N-001/N-007), "tiene cupo" (BR-002), "celular no registrado" (N-004), "nota no firmada" (N-005). El paquete de pruebas del PIA exige al menos tres Specifications combinadas.

**Alternativas.** `if` encadenados dentro de las entidades (reglas dispersas y difíciles de probar); métodos booleanos sueltos (no componibles).

**Decisión.** `Specification` base con `and_/or_/not_` y operadores `& | ~` (`src/domain/specification.py`) y Specifications concretas (`src/domain/specifications.py`). Uso real en el modelo: `Agenda` (`CitaSinTraslape | CitaEsEmergencia`), `Hospitalizacion` (`HospitalizacionTieneCupo`), `ValidadorDuplicidadClienteService` (`CelularNoRegistrado`), `NotaClinica` (`NotaNoFirmada`). Para el paquete de pruebas: `puede_procesarse = ActorActivo & OperacionConDetalle & OperacionAutorizada` y `beneficio_referencia = ActorPreferente & TotalMinimo(1500) & ~PromocionActiva` (`src/domain/operacion.py`), aisladas en un modelo `OperacionVeterinaria` para **no sustituir** las reglas del BRD.

**Consecuencias.** (+) Reglas reutilizables, componibles y testeables. (−) Más clases pequeñas.

**Trazabilidad.** RN-02, RN-04, RN-07, RN-08, RN-12 · `tests/unit/test_specification.py`, `tests/unit/test_reglas_operacion.py` (ejecuta los 120 casos del paquete; evidencia en `docs/evidencias/`).
