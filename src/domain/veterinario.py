from dataclasses import dataclass

from .exceptions import ValidacionDominio


@dataclass
class Veterinario:
    """Identificado por veterinarioId; la cédula respalda la firma de notas (N-005)."""

    id: str
    nombre: str
    cedula: str
    activo: bool = True

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise ValidacionDominio("El veterinario requiere nombre")
        if not self.cedula.strip():
            raise ValidacionDominio("El veterinario requiere cédula profesional")
