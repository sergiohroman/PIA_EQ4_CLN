"""Aggregate ExpedienteClinico (N-002, N-004, N-005).

Raíz: ExpedienteClinico. Contiene Propietario, Mascotas y NotasClinicas.
Invariantes: celular único por propietario (se valida con el Domain Service
ValidadorDuplicidadClienteService) y nota firmada inmutable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from .base import AggregateRoot
from .estados import MAQUINA_NOTA, NotaEstado
from .events import NotaClinicaFirmadaEvent
from .exceptions import NoEncontrado, NotaFirmadaInmutable, ValidacionDominio
from .specifications import NotaNoFirmada
from .value_objects import Celular, FirmaDigital, RecetaMedica
from .veterinario import Veterinario


@dataclass
class Propietario:
    id: str
    nombre: str
    celular: Celular


@dataclass
class Mascota:
    id: str
    nombre: str
    especie: str
    raza: str = ""
    sexo: str = ""
    fecha_nacimiento: date | None = None
    peso: Decimal | None = None
    alergias: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.nombre.strip() or not self.especie.strip():
            raise ValidacionDominio("La mascota requiere nombre y especie")
        if self.peso is not None:
            self.peso = Decimal(str(self.peso))
            if self.peso <= 0:
                raise ValidacionDominio("El peso debe ser mayor a cero")


@dataclass
class NotaClinica:
    id: str
    mascota_id: str
    veterinario_id: str
    diagnostico: str
    notas: str = ""
    receta: RecetaMedica | None = None
    estado: NotaEstado = NotaEstado.BORRADOR
    firma: FirmaDigital | None = None
    creada_en: datetime = field(default_factory=datetime.now)

    def contenido(self) -> str:
        receta = self.receta.a_lista() if self.receta else []
        return f"{self.mascota_id}|{self.diagnostico}|{self.notas}|{receta}"

    def editar(
        self,
        diagnostico: str | None = None,
        notas: str | None = None,
        receta: RecetaMedica | None = None,
    ) -> None:
        if not NotaNoFirmada().is_satisfied_by(self):
            raise NotaFirmadaInmutable()
        if diagnostico is not None:
            self.diagnostico = diagnostico
        if notas is not None:
            self.notas = notas
        if receta is not None:
            self.receta = receta

    def firmar(self, veterinario: Veterinario, ahora: datetime | None = None) -> None:
        if not veterinario.activo:
            raise ValidacionDominio("El veterinario no está activo para firmar")
        self.estado = MAQUINA_NOTA.siguiente(self.estado, "firmar")
        self.firma = FirmaDigital.crear(veterinario.id, self.contenido(), ahora)


class ExpedienteClinico(AggregateRoot):
    def __init__(
        self,
        propietario: Propietario,
        mascotas: list[Mascota] | None = None,
        notas: list[NotaClinica] | None = None,
    ):
        super().__init__()
        self.propietario = propietario
        self.mascotas: list[Mascota] = list(mascotas or [])
        self.notas: list[NotaClinica] = list(notas or [])

    # -- mascotas ---------------------------------------------------------
    def registrar_mascota(self, mascota: Mascota) -> Mascota:
        if any(m.id == mascota.id for m in self.mascotas):
            raise ValidacionDominio("La mascota ya está registrada en el expediente")
        self.mascotas.append(mascota)
        return mascota

    def obtener_mascota(self, mascota_id: str) -> Mascota:
        for mascota in self.mascotas:
            if mascota.id == mascota_id:
                return mascota
        raise NoEncontrado(f"Mascota {mascota_id} no encontrada en el expediente")

    def fusionar_mascotas(self, origen_id: str, destino_id: str) -> Mascota:
        """US-05: consolida el historial del duplicado en el expediente destino."""
        if origen_id == destino_id:
            raise ValidacionDominio("Origen y destino de la fusión deben ser distintos")
        origen = self.obtener_mascota(origen_id)
        destino = self.obtener_mascota(destino_id)
        for nota in self.notas:
            if nota.mascota_id == origen.id:
                nota.mascota_id = destino.id
        for alergia in origen.alergias:
            if alergia not in destino.alergias:
                destino.alergias.append(alergia)
        if destino.peso is None:
            destino.peso = origen.peso
        self.mascotas.remove(origen)
        return destino

    # -- notas clínicas ---------------------------------------------------
    def registrar_nota(
        self,
        nota_id: str,
        mascota_id: str,
        veterinario_id: str,
        diagnostico: str,
        notas: str = "",
        receta: RecetaMedica | None = None,
        peso: Decimal | None = None,
        alergias: list[str] | None = None,
    ) -> NotaClinica:
        """US-07: guarda nota y actualiza peso/alergias del perfil de la mascota."""
        mascota = self.obtener_mascota(mascota_id)
        if not diagnostico.strip():
            raise ValidacionDominio("La nota clínica requiere diagnóstico")
        if peso is not None:
            peso = Decimal(str(peso))
            if peso <= 0:
                raise ValidacionDominio("El peso debe ser mayor a cero")
            mascota.peso = peso
        for alergia in alergias or []:
            if alergia not in mascota.alergias:
                mascota.alergias.append(alergia)
        nota = NotaClinica(nota_id, mascota_id, veterinario_id, diagnostico, notas, receta)
        self.notas.append(nota)
        return nota

    def obtener_nota(self, nota_id: str) -> NotaClinica:
        for nota in self.notas:
            if nota.id == nota_id:
                return nota
        raise NoEncontrado(f"Nota {nota_id} no encontrada")

    def firmar_nota(self, nota_id: str, veterinario: Veterinario) -> NotaClinica:
        nota = self.obtener_nota(nota_id)
        nota.firmar(veterinario)
        self._registrar(NotaClinicaFirmadaEvent(nota.id, nota.mascota_id, veterinario.id))
        return nota

    def modificar_nota(self, nota_id: str, **cambios) -> NotaClinica:
        nota = self.obtener_nota(nota_id)
        nota.editar(**cambios)
        return nota

    def historial(self, mascota_id: str) -> list[NotaClinica]:
        self.obtener_mascota(mascota_id)
        return sorted(
            (n for n in self.notas if n.mascota_id == mascota_id), key=lambda n: n.creada_en
        )
