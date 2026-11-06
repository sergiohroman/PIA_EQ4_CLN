from fastapi import APIRouter, Depends, Query

from src.application.commands import (
    RegistrarIngresoHospitalizacionCommand,
    RegistrarIngresoHospitalizacionHandler,
)
from src.application.dtos import SignosVitalesDto
from src.application.queries import ConsultarOcupacionJaulasQuery

from ..container import Contenedor
from ..dependencies import contenedor
from ..schemas import (
    ErrorOut,
    EstadoJaulasOut,
    IngresoIn,
    SignosIn,
    SignosPendienteOut,
)

router = APIRouter(
    prefix="/hospitalizacion",
    tags=["Hospitalización"],
    responses={404: {"model": ErrorOut}, 409: {"model": ErrorOut}, 422: {"model": ErrorOut}},
)


@router.post("/ingresos", response_model=EstadoJaulasOut, status_code=201,
             summary="CU-04: internar paciente; 409 'Capacidad máxima de jaulas alcanzada' con 10 ocupadas")
def ingresar(datos: IngresoIn, c: Contenedor = Depends(contenedor)):
    handler = RegistrarIngresoHospitalizacionHandler(c.hospitalizacion)
    return handler.handle(
        RegistrarIngresoHospitalizacionCommand(datos.mascota_id, datos.veterinario_id, datos.motivo_ingreso)
    )


@router.post("/altas/{mascota_id}", response_model=EstadoJaulasOut, summary="Dar de alta (libera jaula)")
def alta(mascota_id: str, c: Contenedor = Depends(contenedor)):
    return c.hospitalizacion.dar_alta(mascota_id)


@router.post("/signos-vitales", status_code=201, summary="Registrar signos vitales (US-11)")
def signos(datos: SignosIn, c: Contenedor = Depends(contenedor)):
    return c.hospitalizacion.registrar_signos(
        SignosVitalesDto(datos.mascota_id, datos.temperatura, datos.frecuencia_cardiaca,
                         datos.frecuencia_respiratoria)
    )


@router.get("/signos-pendientes", response_model=list[SignosPendienteOut],
            summary="Pacientes con toma de signos vencida (US-11)")
def pendientes(horas: int = Query(4, ge=1, le=6), c: Contenedor = Depends(contenedor)):
    return c.hospitalizacion.signos_pendientes(horas)


@router.get("/ocupacion", response_model=EstadoJaulasOut, summary="Ocupación de jaulas en tiempo real (US-15)")
def ocupacion(c: Contenedor = Depends(contenedor)):
    return c.q_ocupacion.handle(ConsultarOcupacionJaulasQuery())
