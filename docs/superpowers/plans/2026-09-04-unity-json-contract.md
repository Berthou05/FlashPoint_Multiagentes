# Unity JSON Contract v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every simulation endpoint emit the approved Unity-friendly JSON v1 contract without `null` values.

**Architecture:** Mesa remains the source of truth. `model.py` assigns stable boundary IDs and exports flat Unity DTO data; `server.py` owns the response envelope and state version. Unity keeps its DTOs and sends requests to the server's actual port.

**Tech Stack:** Python 3, Mesa, `http.server`, `unittest`, Unity C#, `JsonUtility`.

## Global Constraints

- Successful simulation responses contain only `api_version`, `state_version`, `events`, and `state`.
- `GET /state` does not advance state version; reset sets 0; doctor/environment phases each add 1.
- `null` is prohibited in simulation responses; absent entity references use `-1`.
- Mesa's MultiGrid remains the sole positional state for board entities.
- Preserve the existing local implementation that makes `/step_doctor` complete one doctor turn.

---

### Task 1: Flat model state with stable boundary IDs

**Files:**
- Modify: `plague_sim/model.py:100-110, 163-185, 930-1025`
- Modify: `tests/test_model.py`

**Interfaces:**
- Produces: `get_boundary_id(cell_a, cell_b) -> int` and `get_state() -> dict` with flat coordinates and `game_status`.
- Consumes: `model.boundaries`, Mesa agent `.pos`, and the existing canonical `edge_key`.

- [ ] **Step 1: Write failing state-contract tests**

```python
state = PlagueSimulationModel(seed=7).get_state()
assert state["active_doctor_id"] >= 0
assert state["game_status"] == "running"
assert {"id", "x", "y", "action_points", "carried_patient_id"} == set(state["doctors"][0])
assert {"id", "ax", "ay", "bx", "by", "damage", "destroyed"} == set(state["walls"][0])
```

- [ ] **Step 2: Run the model tests and verify the new assertions fail**

Run: `python -m unittest tests.test_model -v`

- [ ] **Step 3: Implement the smallest state exporter change**

Store a numeric boundary ID alongside each canonical boundary key, include that
ID in boundary events, replace position lists with coordinate fields and map
all absent export values to contract defaults.

- [ ] **Step 4: Run model tests and verify they pass**

Run: `python -m unittest tests.test_model -v`

### Task 2: Normalize emitted events

**Files:**
- Modify: `plague_sim/model.py:113-120, 369-376, 410-460, 600-740, 817-857`
- Modify: `tests/test_model.py`

**Interfaces:**
- Produces: `get_events() -> list[dict]` containing contract field names.
- Consumes: `get_boundary_id` from Task 1.

- [ ] **Step 1: Write failing event-shape tests**

```python
model = PlagueSimulationModel(seed=7)
events = model.step_doctor()
assert set(events[0]) == {"sequence", "type", "id", "action_points"}
assert set(events[-1]) == {"sequence", "type", "id", "action_points"}
```

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `python -m unittest tests.test_model.TestPlagueSimulationModel.test_doctor_events_use_unity_field_names -v`

- [ ] **Step 3: Implement event fields at their source**

Emit `id`, flat positions and `action_points` directly from model operations;
do not add a lossy server-side event translator. Keep `sequence` and `type`.

- [ ] **Step 4: Run model tests and verify they pass**

Run: `python -m unittest tests.test_model -v`

### Task 3: HTTP envelope and state version

**Files:**
- Modify: `server.py:8-50, 70-105`
- Modify: `tests/test_server.py`

**Interfaces:**
- Produces: every successful simulation response as `{api_version, state_version, events, state}`.
- Consumes: `model.get_state()` and model phase methods from Tasks 1–2.

- [ ] **Step 1: Write failing endpoint-contract tests**

```python
status, response = self.request_json("POST", "/reset", {})
self.assertEqual(set(response), {"api_version", "state_version", "events", "state"})
self.assertEqual(response["state_version"], 0)
self.assertNotIn("null", json.dumps(response))
```

- [ ] **Step 2: Run server tests and verify they fail**

Run: `python -m unittest tests.test_server -v`

- [ ] **Step 3: Implement response builder and version ownership**

Reset the module counter with the model, increment it only after successful
doctor/environment requests, and make `/step`/`/step_complete_turn` advance
twice when both phases complete. Return `state` instead of `game_state`.

- [ ] **Step 4: Run server tests and verify they pass**

Run: `python -m unittest tests.test_server -v`

### Task 4: Unity connection alignment and end-to-end verification

**Files:**
- Modify: `Unity/Assets/Scripts/SimulationConnection.cs:8-95`
- Modify: `README.md`
- Test: `tests/test_server.py`

**Interfaces:**
- Consumes: HTTP contract from Task 3 and existing `SimulationResponse` DTOs.

- [ ] **Step 1: Add a server test for GET state version stability**

```python
self.request_json("POST", "/reset", {})
_, first = self.request_json("GET", "/state")
_, second = self.request_json("GET", "/state")
self.assertEqual(first["state_version"], second["state_version"])
```

- [ ] **Step 2: Run the targeted test and verify it fails before Task 3 is applied**

Run: `python -m unittest tests.test_server.TestServer.test_state_does_not_advance_state_version -v`

- [ ] **Step 3: Point Unity to port 8585 and add POST helpers**

Reuse the existing response deserialization path for `/reset`,
`/step_doctor` and `/step_environment`; Unity continues to animate the
ordered events and synchronizes from `state`.

- [ ] **Step 4: Run all Python tests and inspect a real response**

Run: `python -m unittest discover -s tests -v`

Run: `python -c "import server; server.create_model(seed=7); import json; print(json.dumps({'api_version': 'v1', 'state_version': 0, 'events': [], 'state': server.get_model().get_state()}))"`

- [ ] **Step 5: Commit the implementation**

```powershell
git add server.py plague_sim/model.py tests/test_model.py tests/test_server.py Unity/Assets/Scripts/SimulationConnection.cs README.md
git commit -m "feat: align simulation API with Unity JSON contract"
```
