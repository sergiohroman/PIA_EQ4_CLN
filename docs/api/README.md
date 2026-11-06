# Contrato OpenAPI

El contrato lo genera FastAPI a partir del código. Para exportarlo a este directorio:

```bash
python scripts/exportar_openapi.py   # crea docs/api/openapi.json
```
En ejecución: Swagger UI en `/docs`, ReDoc en `/redoc` y el JSON en `/openapi.json`.
El job de CI exporta `openapi.json` como artefacto en cada *push*.

## Códigos de respuesta
| Código | Significado | Ejemplos |
|--------|-------------|----------|
| 200 / 201 | Éxito / creado | alta de propietario, cita, ingreso |
| 404 | Recurso inexistente | mascota, cita, veterinario, nota |
| 409 | Regla de negocio violada | cliente existente, traslape, 10 jaulas, nota firmada, transición inválida, conflicto de versión |
| 422 | Datos inválidos | celular mal formado, tipo de servicio, signos fuera de rango, cita en el pasado |
