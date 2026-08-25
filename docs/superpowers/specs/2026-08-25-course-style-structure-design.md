# Course-style simulation structure

## Goal

Restore the working Flash Point simulation with the plague-doctor theme while
keeping the code as close as practical to the course reference. Every file and
import must be easy for the team to explain.

## Structure

```text
model.py
doctor.py
pathfinding.py
server.py
```

### `model.py`

Contains the small board-object classes (`Wall`, `Door`, `Patient`,
`Encounter`, `RatSwarm`, and `RatKing`) plus `PlagueSimulationModel`. It owns
board setup, the turn sequence, infestation rules, victory/defeat checks, and
`get_state()` for Unity.

### `doctor.py`

Contains `PlagueDoctorAgent`, its actions, and both decision methods:
`random_strategy()` and `improved_strategy()`. Keeping the strategies here
means a student's complete agent logic can be read in one file.

### `pathfinding.py`

Contains only the Dijkstra function used by the improved strategy. It imports
only `heapq`.

### `server.py`

Contains the small HTTP server Unity calls. It creates the model, advances it,
and returns the result of `model.get_state()` as JSON.

## Deliberate exclusions

The implementation will not use a board-builder class, serializers, event
factories, a strategy package, `TYPE_CHECKING`, postponed annotations, generic
types, or advanced type hints. These patterns are unnecessary for the course
project and make the execution path less direct to explain.

## Imports

Use only the imports needed by the original course approach:

```python
import mesa
import heapq
import random
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
```

Imports are placed only in the file that uses them.

## Data flow

`Unity -> server.py -> PlagueSimulationModel.step() -> PlagueDoctorAgent ->
optional dijkstra() -> get_state() -> Unity`.

## Verification

The completed implementation must run from `server.py`, create a Mesa model,
advance at least one turn, and return JSON state that Unity can consume.
