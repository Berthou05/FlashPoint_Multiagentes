"""Board construction declarations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import PlagueSimulationModel


class BoardBuilder:
    def __init__(self, model: PlagueSimulationModel) -> None:
        pass

    def create_board(self) -> None:
        pass

    def create_perimeter_walls(self) -> None:
        pass

    def create_interior_walls(self) -> None:
        pass

    def create_doors(self) -> None:
        pass

    def create_initial_encounters(self) -> None:
        pass

    def create_initial_infestation(self) -> None:
        pass
