"""Excepciones del dominio expresadas en lenguaje del negocio.

Jerarquía pensada para que la capa API las traduzca a HTTP sin que el dominio
conozca nada de HTTP:
  ValidacionDominio  -> 422
  NoEncontrado       -> 404
  ConflictoDeNegocio -> 409
"""


class DomainError(Exception):
    mensaje_por_defecto = "Error de dominio"

    def __init__(self, mensaje: str | None = None):
        self.mensaje = mensaje or self.mensaje_por_defecto
        super().__init__(self.mensaje)


class ValidacionDominio(DomainError):
    mensaje_por_defecto = "Datos inválidos para el dominio"


class NoEncontrado(DomainError):
    mensaje_por_defecto = "Recurso no encontrado"


class ConflictoDeNegocio(DomainError):
    mensaje_por_defecto = "La operación viola una regla de negocio"


class CapacidadMaximaJaulasAlcanzada(ConflictoDeNegocio):
    """BR-002 / US-12: nunca más de 10 jaulas ocupadas."""

    mensaje_por_defecto = "Capacidad máxima de jaulas alcanzada"


class ClienteExistenteException(ConflictoDeNegocio):
    """N-004 / US-04: el celular ya pertenece a un propietario registrado."""

    mensaje_por_defecto = "Cliente existente"


class TraslapeDeCitas(ConflictoDeNegocio):
    mensaje_por_defecto = "El veterinario ya tiene una cita en ese horario"


class TransicionInvalida(ConflictoDeNegocio):
    mensaje_por_defecto = "Transición de estado no permitida"


class NotaFirmadaInmutable(ConflictoDeNegocio):
    """N-005 / US-08: una nota firmada no se modifica."""

    mensaje_por_defecto = "La nota clínica ya fue firmada y no puede modificarse"


class PacienteYaInternado(ConflictoDeNegocio):
    mensaje_por_defecto = "La mascota ya se encuentra internada"


class PacienteNoInternado(ConflictoDeNegocio):
    mensaje_por_defecto = "La mascota no se encuentra internada"


class ConflictoDeConcurrencia(ConflictoDeNegocio):
    """Bloqueo optimista (ADR-004): otro proceso modificó el agregado."""

    mensaje_por_defecto = "El recurso fue modificado por otra operación; reintente"
