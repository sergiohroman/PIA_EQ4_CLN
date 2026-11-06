"""Punto de entrada FastAPI. Ejecutar con:  uvicorn src.api.main:create_app --factory"""
from datetime import datetime
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.domain.exceptions import ConflictoDeNegocio, DomainError, NoEncontrado, ValidacionDominio

from .container import Contenedor
from .routers import citas, expedientes, hospitalizacion, reportes, veterinarios

PANEL_DIR = Path(__file__).parent / "static"

DESCRIPCION = """
API REST de **VetCare 24** (PIA – Componentes de Lógica de Negocios, Equipo 4).

Reglas principales: celular único por propietario (N-004), nota firmada inmutable (N-005),
máximo 10 jaulas ocupadas (BR-002), emergencias con prioridad máxima (N-007) y
State Machine de citas. Errores: **404** no encontrado, **409** regla de negocio violada,
**422** datos inválidos.

Panel web para el personal de la clínica: [`/app/`](/app/).
"""


def _estatus(error: DomainError) -> int:
    if isinstance(error, NoEncontrado):
        return 404
    if isinstance(error, ConflictoDeNegocio):
        return 409
    if isinstance(error, ValidacionDominio):
        return 422
    return 400


def create_app(database_url: str | None = None, ahora: Callable[[], datetime] = datetime.now) -> FastAPI:
    app = FastAPI(title="VetCare 24 API", version="1.0.0", description=DESCRIPCION)
    app.state.contenedor = Contenedor(database_url, ahora)

    @app.exception_handler(DomainError)
    async def manejar_error_de_dominio(request: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=_estatus(error),
            content={"error": type(error).__name__, "detalle": error.mensaje},
        )

    @app.get("/", include_in_schema=False)
    def raiz() -> RedirectResponse:
        return RedirectResponse(url="/app/")

    @app.get("/app", include_in_schema=False)
    def panel_sin_diagonal() -> RedirectResponse:
        return RedirectResponse(url="/app/")

    @app.get("/health", tags=["Sistema"], summary="Estado del servicio")
    def health() -> dict:
        return {"status": "ok", "servicio": "vetcare24"}

    for modulo in (veterinarios, expedientes, citas, hospitalizacion, reportes):
        app.include_router(modulo.router)
    # Panel web (HTML/CSS/JS estáticos): solo consume la API; las reglas viven en el dominio.
    app.mount("/app", StaticFiles(directory=PANEL_DIR, html=True), name="panel")
    return app
