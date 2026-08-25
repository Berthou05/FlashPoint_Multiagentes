"""Top-level plague simulation model declaration."""

from __future__ import annotations

from .board import BoardBuilder
from .infestation_rules import InfestationRules
from .plague_doctor import PlagueDoctorAgent


class PlagueSimulationModel:
    def __init__(self, width: int | None = None, height: int | None = None) -> None:
        pass

    def step(self) -> None:
        pass

    def create_doctors(self, count: int) -> list[PlagueDoctorAgent]:
        pass

    def add_doctor(self, doctor: PlagueDoctorAgent) -> None:
        pass

    def start_turn(self) -> None:
        pass

    def advance_turn(self) -> None:
        pass

    def end_turn(self) -> None:
        pass

    def get_current_doctor(self) -> PlagueDoctorAgent | None:
        pass

    def run_infestation_phase(self) -> None:
        pass

    def check_game_end(self) -> bool:
        pass

    def has_won(self) -> bool:
        pass

    def has_lost(self) -> bool:
        pass
