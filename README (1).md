# VetCare 24 — PIA Componentes de Lógica de Negocios

Sistema de gestión para una clínica veterinaria 24/7 (agenda, expedientes clínicos, hospitalización y recordatorios) construido con **DDD + Specification + State Machine + API REST**.
UANL · FIME · Equipo 4 · Grupo 002 — David A. Vázquez Fernández, Sergio H. Román Puente, Edelyn N. Carrera García.

| | |
|---|---|
| Repositorio | https://github.com/sergiohroman/PIA_EQ4_CLN |
| Sistema desplegado / Swagger UI | https://vetcare24-api.onrender.com/docs (plan gratuito: la primera petición puede tardar ~50 s en despertar) |

## Stack
Python 3.12 · FastAPI · SQLAlchemy 2.0 · PostgreSQL (SQLite en pruebas) · pytest + pytest-cov · Docker Compose · GitHub Actions. Decisiones en [`docs/architecture`](docs/architecture).

## Estructura
```
docs/            BRD.md, analisis/ (historias+Gherkin, glosario, BPMN), architecture/ (ADRs, UML, decisiones), api/ (OpenAPI), trazabilidad.md, evidencias/
src/domain/          entidades, Value Objects, agregados, eventos, Specifications, State Machine, puertos
src/application/     servicios y casos de uso, DTOs, Commands/Queries, UoW (puerto), bus de eventos
src/infrastructure/  SQLAlchemy (ORM, repositorios, UoW), adaptador WhatsApp
src/api/             controllers REST (FastAPI), esquemas, composition root
tests/               unit/ (dominio) + integration/ (API + BD) + data/ (paquete VetCare 24)
.github/workflows/   CI/CD
```

## Ejecución local
```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn src.api.main:create_app --factory --reload       # usa SQLite local (vetcare.db)
```
Swagger UI: http://localhost:8000/docs

## Docker Compose (DB + App + Tests)
```bash
cp .env.example .env                                     # ajuste las claves
docker compose up --build                                # app + PostgreSQL en :8000
docker compose --profile test run --rm tests             # pruebas contra PostgreSQL
```

## Pruebas
```bash
pytest                    # unitarias + integración; falla si la cobertura es < 80 %
pytest tests/unit --no-cov   # solo dominio, rápido
python scripts/evaluar_casos_vetcare.py   # ejecuta los 120 casos + 20 transiciones del paquete y guarda evidencia
python scripts/exportar_openapi.py        # genera docs/api/openapi.json
```

## Variables de entorno (12-Factor)
Ver [`.env.example`](.env.example). `DATABASE_URL` (si falta, SQLite local), `POSTGRES_*`, `APP_PORT`, `TEST_DATABASE_URL`. Render/Railway inyectan `DATABASE_URL` y `PORT`; el esquema `postgres://` se normaliza automáticamente.

## Despliegue (Render)
1. Suba el repo a GitHub. 2. En Render: **New → Blueprint** y seleccione el repo (usa [`render.yaml`](render.yaml)). 3. Al terminar, abra la URL del servicio + `/docs`. Despliegue actual: https://vetcare24-api.onrender.com/docs

## Guion de demostración (≈5 min)
1. `POST /veterinarios` → crear veterinario. 2. `POST /expedientes` (celular) → repetir el mismo celular: **409 Cliente existente** (US-04).
3. `POST /expedientes/{celular}/mascotas` ×2 → `POST .../fusion` (US-05/06). 4. `POST /mascotas/{id}/notas` con `firmar=true` → `PUT /notas/{id}`: **409 inmutable** (US-07/08).
5. `POST /citas` (vacuna y cirugía: duración distinta) → traslape **409**; `GET /notificaciones` muestra recordatorios (US-01/09/10).
6. `POST /emergencias` → `GET /citas/cola`: emergencia primera (US-03). 7. `POST /citas/{id}/transiciones`: aprobar → aprobar de nuevo **409** (State Machine).
8. Internar 10 mascotas en `POST /hospitalizacion/ingresos` → la 11.ª: **409 «Capacidad máxima de jaulas alcanzada»**; `GET /hospitalizacion/ocupacion` sigue en 10/10 (rollback) (US-12/15).
9. `GET /reportes/vacunas-pendientes?desde=…&hasta=…&formato=csv` → US-13. 10. `POST /reglas/operaciones/evaluar` → Specifications compuestas (AND/OR/NOT). 11. Mostrar `docs/trazabilidad.md` y el CI en verde.

## Alcance parcial declarado
US-09 y US-10 (recordatorios) generan los mensajes por Domain Events en un *outbox* sin proveedor real ni *scheduler*; US-14 entrega la tabla sin gráfico. Detalle en `docs/trazabilidad.md`.

## Trazabilidad y calidad
- Matriz completa: [`docs/trazabilidad.md`](docs/trazabilidad.md). ADRs: [`docs/architecture`](docs/architecture).
- Alcance conocido y deuda técnica: ver `docs/architecture/decisiones_tecnicas.md` §5 (recordatorios con *outbox*, sin proveedor real; sin autenticación/roles).
