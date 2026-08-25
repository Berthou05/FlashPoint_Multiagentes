# Course-style Plague Point Simulation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore a working Mesa plague-doctor version of Flash Point in four plain Python files.

**Architecture:** `model.py` owns the board, simple entities, rules, phases, and Unity state. `doctor.py` owns the Mesa agent and both strategies; `pathfinding.py` only implements Dijkstra; `server.py` is the JSON bridge.

**Tech Stack:** Python, Mesa, `heapq`, `random`, `json`, `http.server`, `logging`, and unittest.

## Global Constraints

- Theme only changes: doctors/rats/rat kings/patients/encounters replace firefighters/fire/smoke/victims/POIs; rules stay unchanged.
- Production files are exactly `model.py`, `doctor.py`, `pathfinding.py`, and `server.py`.
- Avoid type hints, factories, builders, serializers, event objects, and strategy packages.
- Keep both `random_strategy()` and `improved_strategy()` in `doctor.py`.
- Remove `plague_sim/` only after the root implementation and tests pass.

---

### Task 1: Runtime setup and pathfinding

**Files:** Create `pathfinding.py`, create `tests/test_pathfinding.py`, and modify `requirements.txt`.

**Interfaces:** `dijkstra(start, goal, neighbors)` returns the ordered path from start to goal, or `None`. `neighbors(node)` returns `(neighbor, cost)` pairs.

- [ ] **Step 1: Write failing tests.** Add a test graph where `A -> C -> D` costs 2 and `A -> B -> D` costs 6; assert that Dijkstra returns `["A", "C", "D"]`. Add a disconnected-graph test asserting `None`.
- [ ] **Step 2: Run `python -m unittest tests.test_pathfinding -v`.** Confirm the import fails because the module is absent.
- [ ] **Step 3: Write `pathfinding.py`.** Use `heapq` with a `(total_cost, node)` queue, `costs` and `previous` dictionaries; rebuild the path when the goal is popped. Add the Mesa version compatible with `mesa.Agent` and `MultiGrid` to `requirements.txt`.
- [ ] **Step 4: Run `python -m unittest tests.test_pathfinding -v`.** Confirm both tests pass.
- [ ] **Step 5: Commit.** Run `git add pathfinding.py requirements.txt tests/test_pathfinding.py` and `git commit -m "feat: add simple pathfinding helper"`.

### Task 2: Model, board, and infestation

**Files:** Create `model.py` and `tests/test_model.py`.

**Interfaces:** `PlagueSimulationModel(width=8, height=10, num_agents=1, strategy="improved")` provides `is_valid_move`, `manhattan_distance`, `advance_infestation_phase`, `check_game_end`, `step`, and `get_state`.

- [ ] **Step 1: Write failing tests.** Instantiate `PlagueSimulationModel(num_agents=0)`; assert the grid is 8 by 10, `walls` and `rat_swarms` are populated, and `get_state()` contains `doctors`, `rat_swarms`, and `game_stats`.
- [ ] **Step 2: Run `python -m unittest tests.test_model -v`.** Confirm it fails because `model.py` is absent.
- [ ] **Step 3: Write `model.py`.** Move the reference's simple entity classes and its board construction, walls/doors, Manhattan distance, infestation placement, surge propagation, encounter replenishment, loss/win checks, turn loop, and state conversion into `PlagueSimulationModel`. Use internal tuple positions and lists only in `get_state()`. Use the names `patients`, `encounters`, `rat_swarms`, `rat_kings`, `patients_evacuated`, `patients_lost`, and `advance_infestation`.
- [ ] **Step 4: Run `python -m unittest tests.test_model -v`.** Confirm both tests pass.
- [ ] **Step 5: Commit.** Run `git add model.py tests/test_model.py` and `git commit -m "feat: add plague point model and infestation rules"`.

### Task 3: Plague doctor and strategies

**Files:** Create `doctor.py` and `tests/test_doctor.py`; modify `model.py`.

**Interfaces:** `PlagueDoctorAgent(unique_id, model, strategy="random")` extends `mesa.Agent` and provides `step`, `move_action`, `treat_infestation_action`, `carry_patient_action`, `evacuate_patient`, `random_strategy`, and `improved_strategy`.

- [ ] **Step 1: Write failing tests.** With one random doctor, set four action points, move to a legal empty neighbor, and assert one point is spent. Place a doctor at one endpoint of an intact wall and assert it cannot move to the other endpoint.
- [ ] **Step 2: Run `python -m unittest tests.test_doctor -v`.** Confirm it fails because the agent does not exist.
- [ ] **Step 3: Write `doctor.py`.** Move the reference firefighter's direct actions into `PlagueDoctorAgent`, renaming only themed objects. Retain action-point accounting, wall/door checks, loop avoidance, encounter revelation, patient carrying, evacuation, and both strategies. The improved strategy calls Dijkstra; random choice uses `model.random.choice`. Update `model.py` to create doctors with the selected strategy and call the current doctor’s `step()`.
- [ ] **Step 4: Run `python -m unittest tests.test_model tests.test_doctor -v`.** Confirm all tests pass.
- [ ] **Step 5: Commit.** Run `git add model.py doctor.py tests/test_doctor.py` and `git commit -m "feat: add plague doctor actions and strategies"`.

### Task 4: Unity bridge and cleanup

**Files:** Modify `server.py` and `README.md`; create `tests/test_server.py`; delete `plague_sim/`.

**Interfaces:** `create_model(strategy="improved", num_agents=1)` makes the global model. `GET /init`, `GET|POST /step`, and `POST /reset` return JSON containing `game_state`.

- [ ] **Step 1: Write a failing server test.** Call `server.create_model(strategy="random", num_agents=1)`, serialize `server.model.get_state()` with `json.dumps`, and assert it contains one doctor.
- [ ] **Step 2: Run `python -m unittest tests.test_server -v`.** Confirm it fails because `create_model` is not defined.
- [ ] **Step 3: Implement the reference-style HTTP server.** Define module global `model`, `create_model`, `Server._set_response`, `do_OPTIONS`, `do_GET`, `do_POST`, and `run(port=8585)`. Return JSON containing status and `model.get_state()`; allow the Unity CORS headers. Update the README with the four-file structure, `pip install -r requirements.txt`, and `python server.py`. When all root tests are green, delete `plague_sim/` and its obsolete tests.
- [ ] **Step 4: Run `python -m unittest discover -v` and `python -c "import server; server.create_model(); print(server.model.get_state()['game_stats'])"`.** Confirm every test passes and stats print as a dictionary.
- [ ] **Step 5: Commit.** Run `git add server.py README.md tests/test_server.py`, `git rm -r plague_sim`, and `git commit -m "feat: restore course-style Unity simulation"`.
