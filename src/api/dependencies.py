from fastapi import Request

from .container import Contenedor


def contenedor(request: Request) -> Contenedor:
    return request.app.state.contenedor
