"""Caso de uso: evaluar las reglas del paquete de pruebas VetCare 24.

Carga los CSV del paquete (actores, catálogo, operaciones, detalle), arma
OperacionVeterinaria con importes Decimal y evalúa las Specifications compuestas.
También simula las transiciones de `transiciones_prueba.csv` con la State Machine.
"""
from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from src.domain.agenda import Cita
from src.domain.estados import CitaEstado
from src.domain.exceptions import DomainError
from src.domain.operacion import (
    LineaOperacion,
    OperacionVeterinaria,
    beneficio_referencia,
    puede_procesarse,
    recursos_habilitados,
)
from src.domain.value_objects import TipoServicio


def _leer(ruta: Path) -> list[dict]:
    with open(ruta, newline="", encoding="utf-8-sig") as archivo:
        return list(csv.DictReader(archivo))


def cargar_operaciones(directorio: Path) -> dict[str, OperacionVeterinaria]:
    actores = {a["actor_id"]: a for a in _leer(directorio / "actores.csv")}
    catalogo = {c["recurso_id"]: c for c in _leer(directorio / "catalogo.csv")}
    detalle: dict[str, list[LineaOperacion]] = {}
    for fila in _leer(directorio / "detalle_operaciones.csv"):
        recurso = catalogo[fila["recurso_id"]]
        detalle.setdefault(fila["operacion_id"], []).append(
            LineaOperacion(
                recurso_id=fila["recurso_id"],
                precio=Decimal(recurso["precio_mxn"]),
                cantidad=int(fila["cantidad"]),
                habilitado=recurso["habilitado"] == "1",
            )
        )
    operaciones = {}
    for fila in _leer(directorio / "operaciones.csv"):
        actor = actores[fila["actor_id"]]
        operaciones[fila["operacion_id"]] = OperacionVeterinaria(
            operacion_id=fila["operacion_id"],
            actor_id=fila["actor_id"],
            actor_activo=actor["activo"] == "1",
            actor_preferente=actor["es_preferente"] == "1",
            lineas=tuple(detalle.get(fila["operacion_id"], [])),
            promocion_activa=fila["promocion_activa"] == "1",
            autorizado=fila["autorizado"] == "1",
        )
    return operaciones


def evaluar_operacion(operacion: OperacionVeterinaria) -> dict:
    return {
        "operacion_id": operacion.operacion_id,
        "total_mxn": str(operacion.total),
        "puede_procesarse": puede_procesarse().is_satisfied_by(operacion),
        "beneficio_referencia": beneficio_referencia().is_satisfied_by(operacion),
        "recursos_habilitados": recursos_habilitados().is_satisfied_by(operacion),
    }


def simular_transicion(accion_sugerida: str) -> tuple[str, str]:
    """Ejecuta el escenario de transiciones_prueba.csv sobre una Cita nueva.

    Devuelve (estado_final, resultado) donde resultado es el evento o la excepción.
    """
    ahora = datetime(2026, 11, 10, 9, 0)
    cita = Cita("c", "m", "v", TipoServicio.CONSULTA, ahora, ahora)
    secuencias = {
        "aprobar": ["aprobar"],
        "completar": ["completar"],
        "cancelar": ["cancelar"],
        "repetir_aprobacion": ["aprobar", "aprobar"],
        "saltar_estado": ["completar"],
    }
    resultado = ""
    for accion in secuencias[accion_sugerida]:
        try:
            evento = cita.transicionar(accion)
            resultado = f"EVENTO CitaCambioEstadoEvent {evento.estado_anterior}->{evento.estado_nuevo}"
        except DomainError as error:
            resultado = f"EXCEPCION {type(error).__name__}: {error.mensaje}"
            break
    return cita.estado.value if isinstance(cita.estado, CitaEstado) else str(cita.estado), resultado


def ejecutar_casos(directorio: Path) -> tuple[list[dict], list[dict]]:
    """Ejecuta casos_prueba.csv y transiciones_prueba.csv; devuelve filas con resultado."""
    operaciones = cargar_operaciones(directorio)
    casos = []
    for fila in _leer(directorio / "casos_prueba.csv"):
        evaluacion = evaluar_operacion(operaciones[fila["operacion_id"]])
        clave = "puede_procesarse" if fila["tipo_prueba"] == "validar_operacion" else "beneficio_referencia"
        fila = dict(fila)
        fila["resultado_alumno"] = "CUMPLE" if evaluacion[clave] else "NO_CUMPLE"
        fila["evidencia"] = f"total_mxn={evaluacion['total_mxn']}"
        casos.append(fila)
    transiciones = []
    for fila in _leer(directorio / "transiciones_prueba.csv"):
        estado, resultado = simular_transicion(fila["accion_sugerida"])
        fila = dict(fila)
        fila["resultado_alumno"] = estado
        fila["evidencia"] = resultado
        transiciones.append(fila)
    return casos, transiciones
