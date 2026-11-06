# ADR-006: State Machine para Cita y NotaClinica
**Estado:** Aceptada (nueva en el PIA)

**Contexto.** La cita tiene ciclo de vida (U3: Programada, EnAtencion, Completada, Cancelada) y la nota clínica pasa de borrador a firmada (US-08). Las transiciones inválidas (repetir aprobación, saltar estados, operar sobre estados terminales) deben rechazarse con errores del negocio.

**Alternativas.** Campo `estado` con `if` en cada método (invariantes dispersas); `Enum` sin tabla de transiciones (permite saltos).

**Decisión.** `StateMachine` genérica basada en una tabla `(estado, acción) → estado` (`src/domain/estados.py`). `MAQUINA_CITA`: `aprobar` (PROGRAMADA→EN_ATENCION), `completar` (EN_ATENCION→COMPLETADA), `cancelar` (PROGRAMADA/EN_ATENCION→CANCELADA). `MAQUINA_NOTA`: `firmar` (BORRADOR→FIRMADA). Cada transición de cita emite `CitaCambioEstadoEvent`; una transición inválida lanza `TransicionInvalida` (409). Endpoint: `POST /citas/{id}/transiciones`.

**Consecuencias.** (+) El flujo es legible y extensible (agregar estados = agregar filas). (−) Las acciones son cadenas; se limitan en la API con `Literal`.

**Trazabilidad.** RN-07, RN-11 · `tests/unit/test_state_machine.py`, `tests/integration/test_api_citas.py::test_state_machine_via_api`.
