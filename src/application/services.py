"""Application Services (Service Layer, Etapa 4). Solo coordinan; las reglas viven en el dominio."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Callable

from src.domain.agenda import Agenda
from src.domain.exceptions import NoEncontrado, ValidacionDominio
from src.domain.expediente import ExpedienteClinico, Mascota, Propietario
from src.domain.servicios_dominio import (
    AsignadorPrioridadEmergenciaService,
    ValidadorDuplicidadClienteService,
)
from src.domain.value_objects import Celular, ItemReceta, RecetaMedica, SignosVitales, TipoServicio
from src.domain.veterinario import Veterinario

from .dtos import (
    CitaDto,
    ConfirmacionDto,
    EmergenciaDto,
    EstadoJaulasDto,
    ExpedienteDto,
    IngresoInternadoDto,
    MascotaDto,
    MascotaNotaDto,
    NotaDto,
    NotaSalidaDto,
    RespuestaCitaDto,
    SignosVitalesDto,
)
from .unit_of_work import IUnitOfWork

UowFactory = Callable[[], IUnitOfWork]


def _nuevo_id() -> str:
    return uuid.uuid4().hex


def _veterinario_activo(uow: IUnitOfWork, veterinario_id: str) -> Veterinario:
    veterinario = uow.veterinarios.get(veterinario_id)
    if veterinario is None:
        raise NoEncontrado(f"Veterinario {veterinario_id} no encontrado")
    if not veterinario.activo:
        raise ValidacionDominio("El veterinario no está activo")
    return veterinario


def _receta(items) -> RecetaMedica | None:
    if not items:
        return None
    return RecetaMedica(tuple(ItemReceta(i.medicamento, i.dosis, i.indicaciones) for i in items))


# ---------------------------------------------------------------- veterinarios
class VeterinarioApplicationService:
    def __init__(self, uow_factory: UowFactory):
        self._uow_factory = uow_factory

    def registrar(self, nombre: str, cedula: str) -> Veterinario:
        veterinario = Veterinario(_nuevo_id(), nombre, cedula)
        with self._uow_factory() as uow:
            uow.veterinarios.add(veterinario)
            uow.commit()
        return veterinario

    def listar(self) -> list[Veterinario]:
        with self._uow_factory() as uow:
            return uow.veterinarios.listar()


# ----------------------------------------------------------------------- citas
class CitaApplicationService:
    def __init__(self, uow_factory: UowFactory, ahora: Callable[[], datetime] = datetime.now):
        self._uow_factory = uow_factory
        self._ahora = ahora
        self._asignador = AsignadorPrioridadEmergenciaService()

    @staticmethod
    def _tipo(valor: str) -> TipoServicio:
        try:
            return TipoServicio(valor)
        except ValueError:
            raise ValidacionDominio("Tipo de servicio inválido (consulta, vacuna o cirugia)") from None

    @staticmethod
    def _libres(agenda: Agenda, veterinario_id: str, tipo: TipoServicio) -> list[dict]:
        return [
            {"inicio": i, "fin": f} for i, f in agenda.espacios_libres(veterinario_id, tipo)
        ]

    def agendar_cita(self, dto) -> RespuestaCitaDto:
        """CU-01 (N-001)."""
        tipo = self._tipo(dto.tipo)
        if dto.inicio < self._ahora():
            raise ValidacionDominio("No se puede agendar una cita en el pasado")
        with self._uow_factory() as uow:
            _veterinario_activo(uow, dto.veterinario_id)
            expediente = uow.expedientes.get_by_mascota_id(dto.mascota_id)
            if expediente is None:
                raise NoEncontrado(f"Mascota {dto.mascota_id} no encontrada")
            agenda = uow.agendas.get_by_fecha(dto.inicio.date())
            cita = agenda.agendar_cita(
                _nuevo_id(),
                dto.mascota_id,
                tipo,
                dto.veterinario_id,
                dto.inicio,
                celular_propietario=expediente.propietario.celular.valor,
            )
            uow.agendas.save(agenda)
            uow.commit()
            return RespuestaCitaDto(CitaDto.desde(cita), self._libres(agenda, dto.veterinario_id, tipo))

    def registrar_emergencia(self, dto: EmergenciaDto) -> ConfirmacionDto:
        """CU-02 (N-007)."""
        ahora = self._ahora()
        with self._uow_factory() as uow:
            _veterinario_activo(uow, dto.veterinario_id)
            expediente = uow.expedientes.get_by_mascota_id(dto.mascota_id)
            if expediente is None:
                raise NoEncontrado(f"Mascota {dto.mascota_id} no encontrada")
            agenda = uow.agendas.get_by_fecha(ahora.date())
            cita = self._asignador.registrar_emergencia(
                agenda,
                _nuevo_id(),
                dto.mascota_id,
                dto.veterinario_id,
                ahora,
                expediente.propietario.celular.valor,
            )
            uow.agendas.save(agenda)
            uow.commit()
            posicion = [c.id for c in agenda.cola_espera()].index(cita.id) + 1
            return ConfirmacionDto(
                CitaDto.desde(cita), posicion, "Emergencia registrada; se alertó al veterinario"
            )

    def espacios_libres(self, fecha: date, veterinario_id: str, tipo: str) -> list[dict]:
        with self._uow_factory() as uow:
            agenda = uow.agendas.get_by_fecha(fecha)
            return self._libres(agenda, veterinario_id, self._tipo(tipo))

    def cola_espera(self, fecha: date) -> list[CitaDto]:
        with self._uow_factory() as uow:
            return [CitaDto.desde(c) for c in uow.agendas.get_by_fecha(fecha).cola_espera()]

    def transicionar(self, cita_id: str, accion: str) -> CitaDto:
        with self._uow_factory() as uow:
            agenda = uow.agendas.get_by_cita_id(cita_id)
            if agenda is None:
                raise NoEncontrado(f"Cita {cita_id} no encontrada")
            cita = agenda.transicionar_cita(cita_id, accion)
            uow.agendas.save(agenda)
            uow.commit()
            return CitaDto.desde(cita)


# ------------------------------------------------------------------ expedientes
class ExpedienteApplicationService:
    def __init__(self, uow_factory: UowFactory):
        self._uow_factory = uow_factory

    @staticmethod
    def _por_celular(uow: IUnitOfWork, celular: str) -> ExpedienteClinico:
        expediente = uow.expedientes.get_by_celular(Celular(celular))
        if expediente is None:
            raise NoEncontrado("No existe un propietario con ese celular")
        return expediente

    @staticmethod
    def _por_mascota(uow: IUnitOfWork, mascota_id: str) -> ExpedienteClinico:
        expediente = uow.expedientes.get_by_mascota_id(mascota_id)
        if expediente is None:
            raise NoEncontrado(f"Mascota {mascota_id} no encontrada")
        return expediente

    @staticmethod
    def _por_nota(uow: IUnitOfWork, nota_id: str) -> ExpedienteClinico:
        expediente = uow.expedientes.get_by_nota_id(nota_id)
        if expediente is None:
            raise NoEncontrado(f"Nota {nota_id} no encontrada")
        return expediente

    @staticmethod
    def _crear_mascota(dto: MascotaDto) -> Mascota:
        return Mascota(
            _nuevo_id(), dto.nombre, dto.especie, dto.raza, dto.sexo,
            dto.fecha_nacimiento, dto.peso, list(dto.alergias),
        )

    def registrar_propietario(self, nombre: str, celular: str) -> ExpedienteDto:
        """US-04: rechaza si el celular ya existe."""
        if not nombre.strip():
            raise ValidacionDominio("El propietario requiere nombre")
        numero = Celular(celular)
        with self._uow_factory() as uow:
            ValidadorDuplicidadClienteService(uow.expedientes).validar_unico(numero)
            expediente = ExpedienteClinico(Propietario(_nuevo_id(), nombre.strip(), numero))
            uow.expedientes.add(expediente)
            uow.commit()
            return ExpedienteDto.desde(expediente)

    def obtener_expediente(self, celular: str) -> ExpedienteDto:
        with self._uow_factory() as uow:
            return ExpedienteDto.desde(self._por_celular(uow, celular))

    def registrar_mascota(self, celular: str, dto: MascotaDto) -> ExpedienteDto:
        """US-06: nueva mascota bajo el mismo propietario."""
        with self._uow_factory() as uow:
            expediente = self._por_celular(uow, celular)
            expediente.registrar_mascota(self._crear_mascota(dto))
            uow.expedientes.save(expediente)
            uow.commit()
            return ExpedienteDto.desde(expediente)

    def fusionar_mascotas(self, celular: str, origen_id: str, destino_id: str) -> ExpedienteDto:
        """US-05."""
        with self._uow_factory() as uow:
            expediente = self._por_celular(uow, celular)
            expediente.fusionar_mascotas(origen_id, destino_id)
            uow.expedientes.save(expediente)
            uow.commit()
            return ExpedienteDto.desde(expediente)

    def _guardar_nota(self, uow, expediente, mascota_id: str, dto: NotaDto):
        veterinario = _veterinario_activo(uow, dto.veterinario_id)
        nota = expediente.registrar_nota(
            _nuevo_id(), mascota_id, veterinario.id, dto.diagnostico, dto.notas,
            _receta(dto.receta), dto.peso, list(dto.alergias),
        )
        if dto.firmar:
            expediente.firmar_nota(nota.id, veterinario)
        uow.expedientes.save(expediente)
        return nota

    def guardar_nota(self, mascota_id: str, dto: NotaDto) -> NotaSalidaDto:
        """US-07 / US-08 (GuardarNotaClinicaCommand)."""
        with self._uow_factory() as uow:
            expediente = self._por_mascota(uow, mascota_id)
            nota = self._guardar_nota(uow, expediente, mascota_id, dto)
            uow.commit()
            return NotaSalidaDto.desde(nota)

    def vincular_mascota_y_guardar_nota(self, celular: str, dto: MascotaNotaDto) -> ExpedienteDto:
        """CU-03: una sola transacción (Unit of Work) para mascota + nota."""
        with self._uow_factory() as uow:
            expediente = self._por_celular(uow, celular)
            mascota = expediente.registrar_mascota(self._crear_mascota(dto.mascota))
            self._guardar_nota(uow, expediente, mascota.id, dto.nota)
            uow.commit()
            return ExpedienteDto.desde(expediente)

    def firmar_nota(self, nota_id: str, veterinario_id: str) -> NotaSalidaDto:
        with self._uow_factory() as uow:
            expediente = self._por_nota(uow, nota_id)
            veterinario = _veterinario_activo(uow, veterinario_id)
            nota = expediente.firmar_nota(nota_id, veterinario)
            uow.expedientes.save(expediente)
            uow.commit()
            return NotaSalidaDto.desde(nota)

    def modificar_nota(self, nota_id: str, diagnostico=None, notas=None, receta=None) -> NotaSalidaDto:
        with self._uow_factory() as uow:
            expediente = self._por_nota(uow, nota_id)
            nota = expediente.modificar_nota(
                nota_id, diagnostico=diagnostico, notas=notas, receta=_receta(receta)
            )
            uow.expedientes.save(expediente)
            uow.commit()
            return NotaSalidaDto.desde(nota)


# -------------------------------------------------------------- hospitalización
class HospitalizacionApplicationService:
    def __init__(self, uow_factory: UowFactory, ahora: Callable[[], datetime] = datetime.now):
        self._uow_factory = uow_factory
        self._ahora = ahora

    def ingresar_paciente(self, dto: IngresoInternadoDto) -> EstadoJaulasDto:
        """CU-04: si hay 10 jaulas ocupadas se lanza CapacidadMaximaJaulasAlcanzada y se hace rollback."""
        with self._uow_factory() as uow:
            _veterinario_activo(uow, dto.veterinario_id)
            if uow.expedientes.get_by_mascota_id(dto.mascota_id) is None:
                raise NoEncontrado(f"Mascota {dto.mascota_id} no encontrada")
            hospitalizacion = uow.hospitalizacion.obtener_actual()
            hospitalizacion.ingresar_paciente(
                dto.mascota_id, dto.veterinario_id, dto.motivo_ingreso, self._ahora()
            )
            uow.hospitalizacion.save(hospitalizacion)
            uow.commit()
            return EstadoJaulasDto.desde(hospitalizacion)

    def dar_alta(self, mascota_id: str) -> EstadoJaulasDto:
        with self._uow_factory() as uow:
            hospitalizacion = uow.hospitalizacion.obtener_actual()
            hospitalizacion.dar_alta(mascota_id)
            uow.hospitalizacion.save(hospitalizacion)
            uow.commit()
            return EstadoJaulasDto.desde(hospitalizacion)

    def registrar_signos(self, dto: SignosVitalesDto) -> dict:
        with self._uow_factory() as uow:
            hospitalizacion = uow.hospitalizacion.obtener_actual()
            signos = SignosVitales(
                Decimal(str(dto.temperatura)), dto.frecuencia_cardiaca,
                dto.frecuencia_respiratoria, self._ahora(),
            )
            hospitalizacion.registrar_signos(dto.mascota_id, signos)
            uow.hospitalizacion.save(hospitalizacion)
            uow.commit()
            return {"mascota_id": dto.mascota_id, "registrado_en": signos.fecha_registro}

    def signos_pendientes(self, horas: int = 4) -> list[dict]:
        with self._uow_factory() as uow:
            return uow.hospitalizacion.obtener_actual().signos_pendientes(self._ahora(), horas)
