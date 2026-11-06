"""Base de los Aggregate Roots: acumulan Domain Events hasta el commit."""


class AggregateRoot:
    def __init__(self) -> None:
        self._eventos: list = []

    def _registrar(self, evento) -> None:
        self._eventos.append(evento)

    def pull_events(self) -> list:
        eventos, self._eventos = self._eventos, []
        return eventos
