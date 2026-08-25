"""Event payload factory declarations."""

from __future__ import annotations

from typing import Any


def move_event(doctor_id: int, origin: tuple[int, int], destination: tuple[int, int]) -> dict[str, Any]:
    pass


def rats_spawned_event(position: tuple[int, int]) -> dict[str, Any]:
    pass


def rat_king_created_event(position: tuple[int, int]) -> dict[str, Any]:
    pass


def infestation_treated_event(doctor_id: int, position: tuple[int, int]) -> dict[str, Any]:
    pass


def patient_revealed_event(doctor_id: int, position: tuple[int, int]) -> dict[str, Any]:
    pass


def patient_evacuated_event(doctor_id: int, position: tuple[int, int]) -> dict[str, Any]:
    pass


def rat_surge_event(position: tuple[int, int]) -> dict[str, Any]:
    pass
