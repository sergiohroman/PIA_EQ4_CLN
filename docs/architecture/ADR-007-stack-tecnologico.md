# ADR-007: Stack tecnológico y despliegue
**Estado:** Aceptada (nueva en el PIA)

**Contexto.** Plazo corto, necesidad de Swagger automático, aritmética decimal exacta para importes, pruebas rápidas y despliegue reproducible.

**Alternativas.** Java/Spring Boot (JPA, mencionado en U3), C#/.NET (mencionado en la bitácora de IA). Se descartaron por tiempo y por la fricción de configuración para la demo.

**Decisión.** Python 3.12 + **FastAPI** (OpenAPI/Swagger UI automático, validación Pydantic) + **SQLAlchemy 2.0** (ORM; bloqueo optimista con `UPDATE … WHERE version = :leida`) + **PostgreSQL** en producción/Docker y SQLite en memoria para pruebas + **pytest/pytest-cov** + **Docker Compose** (DB + App + Tests) + **GitHub Actions** + **Render** (`render.yaml`). Configuración por variables de entorno (12-Factor).

**Consecuencias.** (+) Entrega rápida y documentación viva. (−) Sin migraciones formales (se usa `create_all`; para evolucionar el esquema se recomienda Alembic).

**Trazabilidad.** RNF-03, RNF-04, RNF-05 · `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `render.yaml`.
