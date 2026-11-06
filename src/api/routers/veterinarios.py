from fastapi import APIRouter, Depends

from ..container import Contenedor
from ..dependencies import contenedor
from ..schemas import ErrorOut, VeterinarioIn, VeterinarioOut

router = APIRouter(tags=["Veterinarios"], responses={409: {"model": ErrorOut}, 422: {"model": ErrorOut}})


@router.post("/veterinarios", response_model=VeterinarioOut, status_code=201, summary="Registrar veterinario")
def registrar(datos: VeterinarioIn, c: Contenedor = Depends(contenedor)):
    v = c.veterinarios.registrar(datos.nombre, datos.cedula)
    return VeterinarioOut(id=v.id, nombre=v.nombre, cedula=v.cedula, activo=v.activo)


@router.get("/veterinarios", response_model=list[VeterinarioOut], summary="Listar veterinarios")
def listar(c: Contenedor = Depends(contenedor)):
    return [VeterinarioOut(id=v.id, nombre=v.nombre, cedula=v.cedula, activo=v.activo)
            for v in c.veterinarios.listar()]
