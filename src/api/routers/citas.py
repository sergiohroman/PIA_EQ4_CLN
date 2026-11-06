from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query

from src.application.dtos import EmergenciaDto, SolicitudCitaDto

from ..container import Contenedor
from ..dependencies import contenedor
from ..schemas import (
    CitaIn,
    CitaOut,
    ConfirmacionOut,
    EmergenciaIn,
    ErrorOut,
    EspacioOut,
    RespuestaCitaOut,
    TransicionIn,
)

router = APIRouter(
    tags=["Agenda y citas"],
    responses={404: {"model": ErrorOut}, 409: {"model": ErrorOut}, 422: {"model": ErrorOut}},
)


@router.post("/citas", response_model=RespuestaCitaOut, status_code=201,
             summary="CU-01: agendar cita con duración automática (US-01); 409 si hay traslape")
def agendar(datos: CitaIn, c: Contenedor = Depends(contenedor)):
    return c.citas.agendar_cita(
        SolicitudCitaDto(datos.mascota_id, datos.veterinario_id, datos.tipo, datos.inicio)
    )


@router.post("/emergencias", response_model=ConfirmacionOut, status_code=201,
             summary="CU-02: registrar emergencia, prioridad máxima y alerta al veterinario (US-03)")
def emergencia(datos: EmergenciaIn, c: Contenedor = Depends(contenedor)):
    return c.citas.registrar_emergencia(EmergenciaDto(datos.mascota_id, datos.veterinario_id))


@router.get("/citas/espacios-libres", response_model=list[EspacioOut],
            summary="Espacios libres del día para un veterinario y servicio (US-02)")
def espacios_libres(
    fecha: date,
    veterinario_id: str,
    tipo: Literal["consulta", "vacuna", "cirugia"] = Query(...),
    c: Contenedor = Depends(contenedor),
):
    return c.citas.espacios_libres(fecha, veterinario_id, tipo)


@router.get("/citas/cola", response_model=list[CitaOut],
            summary="Cola de espera del día: emergencias primero (US-03)")
def cola(fecha: date, c: Contenedor = Depends(contenedor)):
    return c.citas.cola_espera(fecha)


@router.post("/citas/{cita_id}/transiciones", response_model=CitaOut,
             summary="State Machine de la cita: aprobar, completar o cancelar (409 si es inválida)")
def transicionar(cita_id: str, datos: TransicionIn, c: Contenedor = Depends(contenedor)):
    return c.citas.transicionar(cita_id, datos.accion)
