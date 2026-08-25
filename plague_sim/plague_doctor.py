"""Plague doctor agent declaration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import Door, Encounter, Patient, RatKing, RatSwarm, Wall
    from .model import PlagueSimulationModel


class PlagueDoctorAgent:
    def __init__(self, unique_id: int, model: PlagueSimulationModel) -> None:
        pass

    def step(self) -> None:
        pass

    def move(self, destination: tuple[int, int]) -> bool:
        pass

    def get_movement_cost(self, destination: tuple[int, int]) -> int:
        pass

    def treat_infestation(self, position: tuple[int, int] | None = None) -> bool:
        pass

    def break_wall(self, wall: Wall) -> bool:
        pass

    def open_close_door(self, door: Door) -> bool:
        pass

    def carry_patient(self, patient: Patient) -> bool:
        pass

    def reveal_encounter(self, encounter: Encounter) -> Patient | None:
        pass

    def evacuate_patient(self) -> bool:
        pass

    def start_new_turn(self) -> None:
        pass

    def has_actions_remaining(self) -> bool:
        pass

    def spend_action_points(self, amount: int) -> bool:
        pass

    def end_turn(self) -> None:
        pass
