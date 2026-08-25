"""Infestation phase rule declarations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import PlagueSimulationModel


class InfestationRules:
    def __init__(self, model: PlagueSimulationModel) -> None:
        pass

    def advance(self) -> None:
        pass

    def spawn_rats(self, position: tuple[int, int]) -> None:
        pass

    def create_rat_king(self, position: tuple[int, int]) -> None:
        pass

    def convert_adjacent_rats(self, position: tuple[int, int]) -> None:
        pass

    def handle_rat_surge(self, position: tuple[int, int]) -> None:
        pass

    def spread_rat_surge(self, position: tuple[int, int], visited: set[tuple[int, int]] | None = None) -> None:
        pass

    def check_patients_in_danger(self) -> None:
        pass

    def replenish_encounters(self) -> None:
        pass
