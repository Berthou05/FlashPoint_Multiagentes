"""Simulation state serialization declarations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model import PlagueSimulationModel


def serialize_model(model: PlagueSimulationModel) -> dict[str, Any]:
    pass


def serialize_doctors(model: PlagueSimulationModel) -> list[dict[str, Any]]:
    pass


def serialize_patients(model: PlagueSimulationModel) -> list[dict[str, Any]]:
    pass


def serialize_encounters(model: PlagueSimulationModel) -> list[dict[str, Any]]:
    pass


def serialize_walls(model: PlagueSimulationModel) -> list[dict[str, Any]]:
    pass


def serialize_doors(model: PlagueSimulationModel) -> list[dict[str, Any]]:
    pass


def serialize_stats(model: PlagueSimulationModel) -> dict[str, Any]:
    pass
