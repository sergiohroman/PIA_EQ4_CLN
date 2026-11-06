# ADR-001: Domain Model como patrón de lógica de negocio
**Estado:** Aceptada · **Origen:** Actividad 3

**Contexto.** VetCare 24 tiene reglas que deben cumplirse siempre: máximo de 10 jaulas (BR-002, US-12), prioridad de emergencias (N-007, US-03), un cliente por celular (N-004, US-04) y recetas inmutables tras firmarse (N-005, US-08), además de relaciones Propietario–Mascota–Expediente (N-002) y un plazo de 10 semanas (BR-003).

**Alternativas.** *Transaction Script*: rápido, pero repite reglas y las invariantes dependen de validaciones manuales. *Table Module*: no modela bien la identidad de la mascota ni la autoría de la firma.

**Decisión.** Domain Model con tres Aggregate Roots (`ExpedienteClinico`, `Agenda`, `Hospitalizacion`), Value Objects, Domain Services y Domain Events. Los reportes (N-008) se resuelven como Queries de lectura (CQRS básico).

**Consecuencias.** (+) Invariantes protegidas en los agregados y probables sin BD (`tests/unit`). (−) Mayor esfuerzo inicial y curva de aprendizaje.

**Trazabilidad.** N-002, N-004, N-005, N-006, N-007, BR-002, BR-003 · US-03, US-04, US-08, US-12 · `src/domain/`.
