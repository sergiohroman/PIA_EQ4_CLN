import csv
import io
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Response

from src.application.evaluacion_reglas import evaluar_operacion
from src.application.queries import ConsultarProductividadQuery, ConsultarVacunasPendientesQuery
from src.domain.operacion import LineaOperacion, OperacionVeterinaria

from ..container import Contenedor
from ..dependencies import contenedor
from ..schemas import (
    ErrorOut,
    EvaluacionOut,
    EvaluarOperacionIn,
    ProductividadOut,
    VacunaPendienteOut,
)

router = APIRouter(tags=["Reportes y reglas"], responses={422: {"model": ErrorOut}})


@router.get("/reportes/productividad", response_model=list[ProductividadOut],
            summary="Atenciones completadas por veterinario (US-14)")
def productividad(desde: date, hasta: date, c: Contenedor = Depends(contenedor)):
    return c.q_productividad.handle(ConsultarProductividadQuery(desde, hasta))


_COLUMNAS_CSV = ["mascota", "especie", "propietario", "celular", "fecha_cita", "estado", "dias_atraso"]


@router.get("/reportes/vacunas-pendientes", response_model=list[VacunaPendienteOut],
            summary="Mascotas con vacuna atrasada y contacto del dueño (US-13)",
            responses={200: {"content": {"text/csv": {}}, "description": "JSON o CSV según `formato`"}})
def vacunas_pendientes(desde: date, hasta: date, formato: Literal["json", "csv"] = "json",
                       c: Contenedor = Depends(contenedor)):
    filas = c.q_vacunas_pendientes.handle(ConsultarVacunasPendientesQuery(desde, hasta))
    if formato == "json":
        return filas
    salida = io.StringIO()
    escritor = csv.DictWriter(salida, fieldnames=_COLUMNAS_CSV, extrasaction="ignore")
    escritor.writeheader()
    for fila in filas:
        escritor.writerow({**fila, "fecha_cita": fila["fecha_cita"].isoformat()})
    return Response(
        content=salida.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="vacunas_pendientes.csv"'},
    )


@router.post("/reglas/operaciones/evaluar", response_model=EvaluacionOut,
             summary="Evalúa las Specifications compuestas del paquete de pruebas (AND/OR/NOT)")
def evaluar(datos: EvaluarOperacionIn):
    operacion = OperacionVeterinaria(
        operacion_id=datos.operacion_id,
        actor_id="-",
        actor_activo=datos.actor_activo,
        actor_preferente=datos.actor_preferente,
        lineas=tuple(LineaOperacion(l.recurso_id, l.precio, l.cantidad, l.habilitado) for l in datos.lineas),
        promocion_activa=datos.promocion_activa,
        autorizado=datos.autorizado,
    )
    return evaluar_operacion(operacion)


@router.get("/notificaciones", response_model=list[dict],
            summary="Outbox de notificaciones generadas por Domain Events (WhatsApp)")
def notificaciones(c: Contenedor = Depends(contenedor)):
    return list(c.notificaciones.outbox)
