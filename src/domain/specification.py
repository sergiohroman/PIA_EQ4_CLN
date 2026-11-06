"""Patrón Specification con composición AND / OR / NOT (ADR-005)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidato: Any) -> bool: ...

    def and_(self, otra: "Specification") -> "Specification":
        return AndSpecification(self, otra)

    def or_(self, otra: "Specification") -> "Specification":
        return OrSpecification(self, otra)

    def not_(self) -> "Specification":
        return NotSpecification(self)

    __and__ = and_
    __or__ = or_
    __invert__ = not_


class AndSpecification(Specification):
    def __init__(self, izquierda: Specification, derecha: Specification):
        self.izquierda, self.derecha = izquierda, derecha

    def is_satisfied_by(self, candidato: Any) -> bool:
        return self.izquierda.is_satisfied_by(candidato) and self.derecha.is_satisfied_by(candidato)


class OrSpecification(Specification):
    def __init__(self, izquierda: Specification, derecha: Specification):
        self.izquierda, self.derecha = izquierda, derecha

    def is_satisfied_by(self, candidato: Any) -> bool:
        return self.izquierda.is_satisfied_by(candidato) or self.derecha.is_satisfied_by(candidato)


class NotSpecification(Specification):
    def __init__(self, origen: Specification):
        self.origen = origen

    def is_satisfied_by(self, candidato: Any) -> bool:
        return not self.origen.is_satisfied_by(candidato)
