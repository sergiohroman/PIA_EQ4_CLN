# Evidencias

| Archivo | Contenido | Cómo se genera |
|---------|-----------|----------------|
| `resultados_casos_prueba.csv` | 120 casos del paquete VetCare 24 con resultado (`CUMPLE`/`NO_CUMPLE`) y total en MXN calculado con `Decimal` | `python scripts/evaluar_casos_vetcare.py` |
| `resultados_transiciones.csv` | 20 transiciones con estado final y evento/excepción de la State Machine | ídem |
| `pytest_cobertura_local.txt` | Salida de `pytest` en el equipo del alumno: 103 pruebas, 98.19 % de cobertura | `python -m pytest` |
| `coverage.xml` (CI) | Reporte de cobertura (≥ 80 %) | artefacto del job `pruebas` en GitHub Actions |

Pegar aquí además capturas de: Swagger UI desplegado, pipeline CI en verde y `docker compose --profile test run --rm tests`.
