"""Ejecuta casos_prueba.csv y transiciones_prueba.csv del paquete VetCare 24 y guarda evidencia."""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.application.evaluacion_reglas import ejecutar_casos  # noqa: E402

DATOS = RAIZ / "tests" / "data" / "vetcare24"
SALIDA = RAIZ / "docs" / "evidencias"
SALIDA.mkdir(parents=True, exist_ok=True)

casos, transiciones = ejecutar_casos(DATOS)
for nombre, filas in (("resultados_casos_prueba.csv", casos), ("resultados_transiciones.csv", transiciones)):
    with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"{nombre}: {len(filas)} filas")
