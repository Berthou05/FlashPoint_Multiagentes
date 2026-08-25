"""Improved plague doctor strategy declaration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..plague_doctor import PlagueDoctorAgent


class ImprovedStrategy:
    def step(self, doctor: PlagueDoctorAgent) -> None:
        pass

    def rescue_mode(self, doctor: PlagueDoctorAgent) -> None:
        pass

    def search_mode(self, doctor: PlagueDoctorAgent) -> None:
        pass

    def choose_target(self, doctor: PlagueDoctorAgent) -> tuple[int, int] | None:
        pass

    def move_towards_target(self, doctor: PlagueDoctorAgent, target: tuple[int, int]) -> bool:
        pass

    def should_rescue(self, doctor: PlagueDoctorAgent) -> bool:
        pass

    def choose_encounter_target(self, doctor: PlagueDoctorAgent) -> tuple[int, int] | None:
        pass
