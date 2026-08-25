"""Random plague doctor strategy declaration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..plague_doctor import PlagueDoctorAgent


class RandomStrategy:
    def step(self, doctor: PlagueDoctorAgent) -> None:
        pass

    def choose_action(self, doctor: PlagueDoctorAgent) -> str | None:
        pass

    def choose_move_destination(self, doctor: PlagueDoctorAgent) -> tuple[int, int] | None:
        pass

    def choose_infestation_target(self, doctor: PlagueDoctorAgent) -> tuple[int, int] | None:
        pass
