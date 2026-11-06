from fastapi import APIRouter, Depends

from src.application.commands import GuardarNotaClinicaCommand, GuardarNotaClinicaHandler
from src.application.dtos import ItemRecetaDto, MascotaDto, MascotaNotaDto, NotaDto
from src.application.queries import ConsultarHistorialMascotaQuery

from ..container import Contenedor
from ..dependencies import contenedor
from ..schemas import (
    ErrorOut,
    ExpedienteOut,
    FirmaIn,
    FusionIn,
    HistorialOut,
    ItemRecetaIn,
    MascotaIn,
    MascotaNotaIn,
    NotaIn,
    NotaOut,
    NotaUpdateIn,
    PropietarioIn,
)

router = APIRouter(
    tags=["Expedientes clínicos"],
    responses={404: {"model": ErrorOut}, 409: {"model": ErrorOut}, 422: {"model": ErrorOut}},
)


def _mascota(m: MascotaIn) -> MascotaDto:
    return MascotaDto(m.nombre, m.especie, m.raza, m.sexo, m.fecha_nacimiento, m.peso, list(m.alergias))


def _receta(items: list[ItemRecetaIn] | None) -> list[ItemRecetaDto]:
    return [ItemRecetaDto(i.medicamento, i.dosis, i.indicaciones) for i in (items or [])]


def _nota(n: NotaIn) -> NotaDto:
    return NotaDto(n.veterinario_id, n.diagnostico, n.notas, _receta(n.receta), n.peso,
                   list(n.alergias), n.firmar)


@router.post("/expedientes", response_model=ExpedienteOut, status_code=201,
             summary="Registrar propietario (US-04: 409 si el celular ya existe)")
def registrar_propietario(datos: PropietarioIn, c: Contenedor = Depends(contenedor)):
    return c.expedientes.registrar_propietario(datos.nombre, datos.celular)


@router.get("/expedientes/{celular}", response_model=ExpedienteOut, summary="Buscar expediente por celular")
def obtener_expediente(celular: str, c: Contenedor = Depends(contenedor)):
    return c.expedientes.obtener_expediente(celular)


@router.post("/expedientes/{celular}/mascotas", response_model=ExpedienteOut, status_code=201,
             summary="Vincular mascota al propietario (US-06)")
def registrar_mascota(celular: str, datos: MascotaIn, c: Contenedor = Depends(contenedor)):
    return c.expedientes.registrar_mascota(celular, _mascota(datos))


@router.post("/expedientes/{celular}/mascotas/fusion", response_model=ExpedienteOut,
             summary="Fusionar expedientes de mascota duplicados (US-05)")
def fusionar(celular: str, datos: FusionIn, c: Contenedor = Depends(contenedor)):
    return c.expedientes.fusionar_mascotas(celular, datos.origen_id, datos.destino_id)


@router.post("/expedientes/{celular}/mascotas-con-nota", response_model=ExpedienteOut, status_code=201,
             summary="CU-03: vincular mascota y guardar nota médica en una sola transacción")
def vincular_y_guardar(celular: str, datos: MascotaNotaIn, c: Contenedor = Depends(contenedor)):
    dto = MascotaNotaDto(_mascota(datos.mascota), _nota(datos.nota))
    return c.expedientes.vincular_mascota_y_guardar_nota(celular, dto)


@router.get("/mascotas/{mascota_id}/historial", response_model=HistorialOut,
            summary="Consultar historial de la mascota (Query, CE-002)")
def historial(mascota_id: str, c: Contenedor = Depends(contenedor)):
    return c.q_historial.handle(ConsultarHistorialMascotaQuery(mascota_id))


@router.post("/mascotas/{mascota_id}/notas", response_model=NotaOut, status_code=201,
             summary="Guardar nota clínica y receta (US-07); firmar=true => 'Guardar y Firmar' (US-08)")
def guardar_nota(mascota_id: str, datos: NotaIn, c: Contenedor = Depends(contenedor)):
    handler = GuardarNotaClinicaHandler(c.expedientes)
    return handler.handle(GuardarNotaClinicaCommand(mascota_id, _nota(datos)))


@router.put("/notas/{nota_id}", response_model=NotaOut,
            summary="Modificar nota en borrador (409 si ya está firmada, US-08)")
def modificar_nota(nota_id: str, datos: NotaUpdateIn, c: Contenedor = Depends(contenedor)):
    receta = _receta(datos.receta) if datos.receta is not None else None
    return c.expedientes.modificar_nota(nota_id, datos.diagnostico, datos.notas, receta)


@router.post("/notas/{nota_id}/firma", response_model=NotaOut, summary="Firmar nota clínica (US-08)")
def firmar(nota_id: str, datos: FirmaIn, c: Contenedor = Depends(contenedor)):
    return c.expedientes.firmar_nota(nota_id, datos.veterinario_id)
