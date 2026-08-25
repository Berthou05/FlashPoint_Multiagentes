"""Entity declarations for the plague simulation."""

from __future__ import annotations

class Patient:
    def __init__(self, position: tuple[int, int] | None = None) -> None:
        pass


class Encounter:
    def __init__(self, position: tuple[int, int] | None = None) -> None:
        pass


class RatSwarm:
    def __init__(self, position: tuple[int, int] | None = None) -> None:
        pass


class RatKing:
    def __init__(self, position: tuple[int, int] | None = None) -> None:
        pass


class Wall:
    def __init__(self, start: tuple[int, int] | None = None, end: tuple[int, int] | None = None) -> None:
        pass


class Door:
    def __init__(self, position: tuple[int, int] | None = None, is_open: bool = False) -> None:
        pass


class Sign:
    def __init__(self, position: tuple[int, int] | None = None, label: str = "") -> None:
        pass
