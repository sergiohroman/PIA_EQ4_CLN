"""Implementaciones SQLAlchemy de los puertos de repositorio (ADR-002)."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.agenda import Agenda, Cita
from src.domain.estados import CitaEstado, NotaEstado
from src.domain.exceptions import (
    ClienteExistenteException,
    ConflictoDeConcurrencia,
    ConflictoDeNegocio,
)
from src.domain.expediente import ExpedienteClinico, Mascota, NotaClinica, Propietario
from src.domain.hospitalizacion import Hospitalizacion, Jaula
from src.domain.repositories import (
    IAgendaRepository,
    IExpedienteRepository,
    IHospitalizacionRepository,
    IVeterinarioRepository,
)
from src.domain.value_objects import (
    Celular,
    FirmaDigital,
    RecetaMedica,
    SignosVitales,
    TipoServicio,
)
from src.domain.veterinario import Veterinario

from .orm import (
    CitaORM,
    HospitalizacionORM,
    JaulaORM,
    MascotaORM,
    NotaClinicaORM,
    PropietarioORM,
    SignosVitalesORM,
    VeterinarioORM,
)


class _RepoBase:
    """Registra los agregados tocados para que la UoW publique sus eventos tras el commit."""

    def __init__(self, session: Session, vistos: list):
        self.session = session
        self._vistos = vistos

    def _seguir(self, agregado):
        if not any(a is agregado for a in self._vistos):
            self._vistos.append(agregado)
        return agregado


# ----------------------------------------------------------------- Expediente
class SqlExpedienteRepository(_RepoBase, IExpedienteRepository):
    def _hidratar(self, fila: PropietarioORM) -> ExpedienteClinico:
        mascotas_orm = self.session.scalars(
            select(MascotaORM).where(MascotaORM.propietario_id == fila.id)
        ).all()
        ids = [m.id for m in mascotas_orm]
        notas_orm = (
            self.session.scalars(select(NotaClinicaORM).where(NotaClinicaORM.mascota_id.in_(ids))).all()
            if ids
            else []
        )
        mascotas = [
            Mascota(
                id=m.id, nombre=m.nombre, especie=m.especie, raza=m.raza, sexo=m.sexo,
                fecha_nacimiento=m.fecha_nacimiento, peso=m.peso, alergias=list(m.alergias or []),
            )
            for m in mascotas_orm
        ]
        notas = [
            NotaClinica(
                id=n.id, mascota_id=n.mascota_id, veterinario_id=n.veterinario_id,
                diagnostico=n.diagnostico, notas=n.notas,
                receta=RecetaMedica.desde_lista(n.receta) if n.receta else None,
                estado=NotaEstado(n.estado),
                firma=FirmaDigital(n.firma_id_usuario, n.firma_sello, n.firma_en) if n.firma_sello else None,
                creada_en=n.creada_en,
            )
            for n in notas_orm
        ]
        propietario = Propietario(fila.id, fila.nombre, Celular(fila.celular))
        return self._seguir(ExpedienteClinico(propietario, mascotas, notas))

    def _persistir(self, exp: ExpedienteClinico) -> None:
        p = exp.propietario
        try:
            self.session.merge(PropietarioORM(id=p.id, nombre=p.nombre, celular=p.celular.valor))
            self.session.flush()
        except IntegrityError as error:
            raise ClienteExistenteException() from error
        for m in exp.mascotas:
            self.session.merge(
                MascotaORM(
                    id=m.id, propietario_id=p.id, nombre=m.nombre, especie=m.especie, raza=m.raza,
                    sexo=m.sexo, fecha_nacimiento=m.fecha_nacimiento, peso=m.peso,
                    alergias=list(m.alergias),
                )
            )
        self.session.flush()
        for n in exp.notas:
            self.session.merge(
                NotaClinicaORM(
                    id=n.id, mascota_id=n.mascota_id, veterinario_id=n.veterinario_id,
                    diagnostico=n.diagnostico, notas=n.notas,
                    receta=n.receta.a_lista() if n.receta else None, estado=n.estado.value,
                    firma_id_usuario=n.firma.id_usuario if n.firma else None,
                    firma_sello=n.firma.sello if n.firma else None,
                    firma_en=n.firma.firmado_en if n.firma else None,
                    creada_en=n.creada_en,
                )
            )
        self.session.flush()
        vigentes = [m.id for m in exp.mascotas]
        condicion = [MascotaORM.propietario_id == p.id]
        if vigentes:
            condicion.append(MascotaORM.id.not_in(vigentes))
        self.session.execute(delete(MascotaORM).where(*condicion))  # mascotas fusionadas
        self.session.flush()

    def add(self, expediente: ExpedienteClinico) -> None:
        self._persistir(expediente)
        self._seguir(expediente)

    def save(self, expediente: ExpedienteClinico) -> None:
        self._persistir(expediente)
        self._seguir(expediente)

    def existe_celular(self, celular: Celular) -> bool:
        total = self.session.scalar(
            select(func.count()).select_from(PropietarioORM).where(PropietarioORM.celular == celular.valor)
        )
        return bool(total)

    def get_by_celular(self, celular: Celular) -> ExpedienteClinico | None:
        fila = self.session.scalar(select(PropietarioORM).where(PropietarioORM.celular == celular.valor))
        return self._hidratar(fila) if fila else None

    def get_by_mascota_id(self, mascota_id: str) -> ExpedienteClinico | None:
        mascota = self.session.get(MascotaORM, mascota_id)
        if mascota is None:
            return None
        return self._hidratar(self.session.get(PropietarioORM, mascota.propietario_id))

    def get_by_nota_id(self, nota_id: str) -> ExpedienteClinico | None:
        nota = self.session.get(NotaClinicaORM, nota_id)
        return self.get_by_mascota_id(nota.mascota_id) if nota else None


# --------------------------------------------------------------------- Agenda
class SqlAgendaRepository(_RepoBase, IAgendaRepository):
    @staticmethod
    def _a_dominio(c: CitaORM) -> Cita:
        return Cita(
            id=c.id, mascota_id=c.mascota_id, veterinario_id=c.veterinario_id,
            tipo=TipoServicio(c.tipo), inicio=c.inicio, fin=c.fin, estado=CitaEstado(c.estado),
            es_emergencia=c.es_emergencia, requiere_reprogramacion=c.requiere_reprogramacion,
            celular_propietario=c.celular_propietario,
        )

    def get_by_fecha(self, fecha: date) -> Agenda:
        filas = self.session.scalars(
            select(CitaORM).where(CitaORM.fecha == fecha).order_by(CitaORM.inicio)
        ).all()
        return self._seguir(Agenda(fecha, [self._a_dominio(f) for f in filas]))

    def get_by_cita_id(self, cita_id: str) -> Agenda | None:
        fila = self.session.get(CitaORM, cita_id)
        return self.get_by_fecha(fila.fecha) if fila else None

    def save(self, agenda: Agenda) -> None:
        for c in agenda.citas:
            self.session.merge(
                CitaORM(
                    id=c.id, fecha=c.inicio.date(), mascota_id=c.mascota_id,
                    veterinario_id=c.veterinario_id, tipo=c.tipo.value, inicio=c.inicio, fin=c.fin,
                    estado=c.estado.value, es_emergencia=c.es_emergencia,
                    requiere_reprogramacion=c.requiere_reprogramacion,
                    celular_propietario=c.celular_propietario,
                )
            )
        self.session.flush()
        self._seguir(agenda)

    def listar_rango(self, desde: date, hasta: date) -> list[Cita]:
        filas = self.session.scalars(
            select(CitaORM).where(CitaORM.fecha >= desde, CitaORM.fecha <= hasta)
        ).all()
        return [self._a_dominio(f) for f in filas]


# ------------------------------------------------------------ Hospitalización
class SqlHospitalizacionRepository(_RepoBase, IHospitalizacionRepository):
    def _version_actual(self) -> int:
        """Lee la versión directo de la BD (sin pasar por el identity map)."""
        version = self.session.execute(
            select(HospitalizacionORM.version).where(HospitalizacionORM.id == 1)
        ).scalar_one_or_none()
        if version is None:
            raise RuntimeError("Base de datos sin inicializar: ejecute inicializar_db()")
        return int(version)

    def obtener_actual(self) -> Hospitalizacion:
        version = self._version_actual()
        jaulas_orm = self.session.scalars(select(JaulaORM).order_by(JaulaORM.numero)).all()
        jaulas = [Jaula(j.numero, j.mascota_id, j.veterinario_id, j.motivo, j.ingreso) for j in jaulas_orm]
        signos: dict[str, list[SignosVitales]] = {}
        for j in jaulas_orm:
            if j.mascota_id is None:
                continue
            lecturas = self.session.scalars(
                select(SignosVitalesORM)
                .where(
                    SignosVitalesORM.mascota_id == j.mascota_id,
                    SignosVitalesORM.fecha_registro >= j.ingreso,
                )
                .order_by(SignosVitalesORM.fecha_registro)
            ).all()
            signos[j.mascota_id] = [
                SignosVitales(
                    Decimal(str(s.temperatura)), s.frecuencia_cardiaca,
                    s.frecuencia_respiratoria, s.fecha_registro,
                )
                for s in lecturas
            ]
        return self._seguir(Hospitalizacion(jaulas, signos, version=version))

    def get_ocupacion_actual(self) -> int:
        return int(
            self.session.scalar(
                select(func.count()).select_from(JaulaORM).where(JaulaORM.mascota_id.is_not(None))
            )
            or 0
        )

    def save(self, hospitalizacion: Hospitalizacion) -> None:
        # Bloqueo optimista (ADR-004): solo se escribe si nadie cambió la versión que leímos.
        resultado = self.session.execute(
            update(HospitalizacionORM)
            .where(HospitalizacionORM.id == 1, HospitalizacionORM.version == hospitalizacion.version)
            .values(version=hospitalizacion.version + 1, actualizado_en=datetime.now())
            .execution_options(synchronize_session=False)
        )
        if resultado.rowcount != 1:
            raise ConflictoDeConcurrencia()
        hospitalizacion.version += 1
        for j in hospitalizacion.jaulas:
            orm = self.session.get(JaulaORM, j.numero)
            orm.mascota_id, orm.veterinario_id = j.mascota_id, j.veterinario_id
            orm.motivo, orm.ingreso = j.motivo, j.ingreso
        for mascota_id, s in hospitalizacion.pull_signos_nuevos():
            self.session.add(
                SignosVitalesORM(
                    mascota_id=mascota_id, temperatura=s.temperatura,
                    frecuencia_cardiaca=s.frecuencia_cardiaca,
                    frecuencia_respiratoria=s.frecuencia_respiratoria,
                    fecha_registro=s.fecha_registro,
                )
            )
        self.session.flush()
        self._seguir(hospitalizacion)


# --------------------------------------------------------------- Veterinarios
class SqlVeterinarioRepository(_RepoBase, IVeterinarioRepository):
    def add(self, veterinario: Veterinario) -> None:
        self.session.add(
            VeterinarioORM(
                id=veterinario.id, nombre=veterinario.nombre,
                cedula=veterinario.cedula, activo=veterinario.activo,
            )
        )
        try:
            self.session.flush()
        except IntegrityError as error:
            raise ConflictoDeNegocio("Ya existe un veterinario con esa cédula") from error

    @staticmethod
    def _a_dominio(v: VeterinarioORM) -> Veterinario:
        return Veterinario(v.id, v.nombre, v.cedula, v.activo)

    def get(self, veterinario_id: str) -> Veterinario | None:
        fila = self.session.get(VeterinarioORM, veterinario_id)
        return self._a_dominio(fila) if fila else None

    def listar(self) -> list[Veterinario]:
        filas = self.session.scalars(select(VeterinarioORM).order_by(VeterinarioORM.nombre)).all()
        return [self._a_dominio(f) for f in filas]
