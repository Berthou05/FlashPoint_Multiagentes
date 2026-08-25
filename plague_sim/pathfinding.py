"""Pathfinding function declarations."""

from __future__ import annotations

import heapq
from collections.abc import Callable, Iterable
from typing import TypeVar

Node = TypeVar("Node")


def dijkstra(
    start: Node,
    goal: Node,
    neighbors: Callable[[Node], Iterable[tuple[Node, int]]],
) -> list[Node] | None:
    pass
