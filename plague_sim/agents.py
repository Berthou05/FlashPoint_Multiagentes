import heapq

import mesa

from .entities import Door, POI, Patient, RatKing, RatSwarm, Wall


class PlagueDoctorAgent(mesa.Agent):
    """Doctor that decides and executes actions on the shared board."""

    # ==========================================================
    # GENERAL LOGIC
    # ==========================================================

    MAX_ACTION_POINTS = 8
    WALL_BREAK_PENALTY = 4
    TARGET_CLAIM_PENALTY = 0
    RESCUE_BONUS = 6
    CONTROLLED_RAT_KING_LIMIT = 2

    ACTION_COSTS = {
        "move": 1,
        "open_door": 1,
        "close_door": 1,
        "damage_wall": 2,
        "treat_rat_swarm": 1,
        "reduce_rat_king": 1,
        "treat_rat_king": 2,
        "pick_up_patient": 0,
        "drop_patient": 0,
        "move_carrying_patient": 2,
    }

    def __init__(self, model, strategy="random"):
        super().__init__(model)
        self.strategy = strategy
        self.action_points = 0
        self.carried_patient = None
        self.turn_completed = False
        self.current_task = None
        self.recalculate_task = True

    def spend_ap(self, cost):
        if self.action_points < cost:
            return False
        self.action_points -= cost
        return True

    def get_transition_cost(self, current, target):
        """Real AP cost of a normal move from the Doctor's current state."""
        if not self.model.are_neighbors(current, target):
            return float("inf")

        move_cost = self.ACTION_COSTS[
            "move_carrying_patient" if self.carried_patient is not None else "move"
        ]
        boundary = self.model.get_boundary(current, target)

        if boundary is None or boundary.is_passable:
            return move_cost
        return float("inf")

    def start_turn(self):
        self.action_points = min(self.action_points + 4, self.MAX_ACTION_POINTS)
        self.turn_completed = False
        self.recalculate_task = True

    def end_turn(self):
        self.turn_completed = True

    def get_available_actions(self):
        """Return legal actions the Doctor can currently afford."""
        actions = []
        neighbors = sorted(self.model.get_neighbors(self.pos))

        for target in neighbors:
            boundary = self.model.get_boundary(self.pos, target)
            infestation = self.model.get_entity(target, (RatSwarm, RatKing))

            if self.model.can_cross(self.pos, target) and not isinstance(infestation, RatKing):
                actions.append(("move", target))

            if isinstance(boundary, Door):
                if not boundary.is_passable:
                    actions.append(("open_door", target))
                elif boundary.is_open and not boundary.is_destroyed:
                    actions.append(("close_door", target))
            elif isinstance(boundary, Wall) and not boundary.is_destroyed:
                actions.append(("damage_wall", target))

        treatment_positions = [self.pos] + [target for target in neighbors if self.model.can_cross(self.pos, target)]
        for position in treatment_positions:
            infestation = self.model.get_entity(position, (RatSwarm, RatKing))
            if isinstance(infestation, RatSwarm):
                actions.append(("treat_rat_swarm", infestation))
            elif isinstance(infestation, RatKing):
                actions.append(("reduce_rat_king", infestation))
                actions.append(("treat_rat_king", infestation))

        if self.carried_patient is None:
            for patient in self.model.grid.get_cell_list_contents([self.pos]):
                if isinstance(patient, Patient):
                    actions.append(("pick_up_patient", patient))
        elif self.model.is_exterior_position(self.pos):
            actions.append(("drop_patient", None))

        return [
            action for action in actions
            if self.action_points >= (
                self.get_transition_cost(self.pos, action[1])
                if action[0] == "move"
                else self.ACTION_COSTS[action[0]]
            )
        ]

    def execute_action(self, action):
        """Execute one legal action returned by a strategy."""
        kind, target = action
        can_drop_carried_patient = kind == "drop_patient" and target is None and self.carried_patient is not None

        if action not in self.get_available_actions() and not can_drop_carried_patient:
            return False

        if kind == "move":
            self.spend_ap(self.get_transition_cost(self.pos, target))
            previous = self.pos
            self.model.grid.move_agent(self, target)
            self.model.emit_event(
                "doctor_moved",
                id=self.unique_id,
                from_x=previous[0],
                from_y=previous[1],
                to_x=target[0],
                to_y=target[1],
                action_points=self.action_points,
            )
            poi = self.model.get_entity(target, POI)
            if poi is not None:
                self.model.reveal_poi(poi)
            return True

        if kind == "open_door":
            self.spend_ap(self.ACTION_COSTS[kind])
            self.model.get_boundary(self.pos, target).open()
            self.model.emit_event("door_opened", id=self.model.get_boundary_id(self.pos, target))
            return True

        if kind == "close_door":
            self.spend_ap(self.ACTION_COSTS[kind])
            self.model.get_boundary(self.pos, target).close()
            self.model.emit_event("door_closed", id=self.model.get_boundary_id(self.pos, target))
            return True

        if kind == "damage_wall":
            self.spend_ap(self.ACTION_COSTS[kind])
            self.model.damage_boundary(self.pos, target)
            return True

        if kind == "reduce_rat_king":
            self.spend_ap(self.ACTION_COSTS[kind])
            self.model.demote_rat_king(target)
            return True

        if kind in ("treat_rat_swarm", "treat_rat_king"):
            self.spend_ap(self.ACTION_COSTS[kind])
            self.model.remove_infestation(target)
            return True

        if kind == "pick_up_patient":
            self.spend_ap(self.ACTION_COSTS[kind])
            self.model.grid.remove_agent(target)
            self.carried_patient = target
            self.model.emit_event("patient_picked_up", id=target.unique_id)
            return True

        if kind == "drop_patient":
            self.spend_ap(self.ACTION_COSTS[kind])
            patient = self.carried_patient
            if self.model.is_exterior_position(self.pos):
                self.model.rescue_patient(patient)
            else:
                self.model.grid.place_agent(patient, self.pos)
                self.carried_patient = None
                self.model.emit_event("patient_dropped", id=patient.unique_id, x=self.pos[0], y=self.pos[1])
            return True

        return False

    # ==========================================================
    # RANDOM STRATEGY
    # ==========================================================

    def step_random(self):
        actions = self.get_available_actions()

        if not actions:
            self.end_turn()
            return False

        if not self.execute_action(self.model.random.choice(actions)):
            raise RuntimeError("A selected legal Doctor action could not execute.")

        return True

    # ==========================================================
    # INTELLIGENT STRATEGY
    # ==========================================================

    def get_tasks(self):
        """Return every currently relevant objective visible to the Doctor."""
        if self.carried_patient is not None:
            return [{"kind": "rescue_carried", "target": self.carried_patient}]

        tasks = []

        for entity in self.model.agents:
            if entity.pos is None:
                continue

            if isinstance(entity, Patient):
                tasks.append({"kind": "rescue", "target": entity})
            elif isinstance(entity, POI):
                tasks.append({"kind": "investigate", "target": entity})
            elif isinstance(entity, RatKing):
                tasks.append({"kind": "treat_rat_king", "target": entity})
            elif isinstance(entity, RatSwarm):
                tasks.append({"kind": "treat_rat_swarm", "target": entity})

        return tasks

    def get_path_transition(self, current, target, carrying=False, cleared_edges=None):
        """Return Dijkstra cost and actions needed to safely cross one neighboring edge."""
        if not self.model.are_neighbors(current, target):
            return None

        cleared_edges = cleared_edges or set()
        actions = []
        ap_cost = 0
        penalty = 0
        move_cost = self.ACTION_COSTS["move_carrying_patient" if carrying else "move"]
        boundary = self.model.get_boundary(current, target)
        edge = self.model.edge_key(current, target)

        if edge not in cleared_edges:
            if isinstance(boundary, Door) and not boundary.is_passable:
                actions.append(("open_door", target))
                ap_cost += self.ACTION_COSTS["open_door"]

            elif isinstance(boundary, Wall) and not boundary.is_destroyed:
                hits = boundary.MAX_DAMAGE - boundary.damage
                actions.extend([("damage_wall", target)] * hits)
                ap_cost += hits * self.ACTION_COSTS["damage_wall"]
                penalty += self.WALL_BREAK_PENALTY

        infestation = self.model.get_entity(target, (RatSwarm, RatKing))

        if isinstance(infestation, RatSwarm):
            actions.append(("treat_rat_swarm", infestation))
            ap_cost += self.ACTION_COSTS["treat_rat_swarm"]

        elif isinstance(infestation, RatKing):
            actions.append(("treat_rat_king", infestation))
            ap_cost += self.ACTION_COSTS["treat_rat_king"]

        actions.append(("move", target))
        ap_cost += move_cost

        return {
            "score": ap_cost + penalty,
            "ap": ap_cost,
            "penalty": penalty,
            "actions": actions,
        }

    def dijkstra(self, start, carrying=False, cleared_edges=None):
        """Calculate the cheapest weighted route from start to every board cell."""
        scores = {start: 0}
        ap_costs = {start: 0}
        penalties = {start: 0}
        previous = {}
        previous_actions = {}
        queue = [(0, start)]

        while queue:
            current_score, current = heapq.heappop(queue)

            if current_score != scores[current]:
                continue

            for neighbor in self.model.get_neighbors(current):
                transition = self.get_path_transition(current, neighbor, carrying, cleared_edges)
                if transition is None:
                    continue

                new_score = current_score + transition["score"]

                if neighbor not in scores or new_score < scores[neighbor]:
                    scores[neighbor] = new_score
                    ap_costs[neighbor] = ap_costs[current] + transition["ap"]
                    penalties[neighbor] = penalties[current] + transition["penalty"]
                    previous[neighbor] = current
                    previous_actions[neighbor] = transition["actions"]
                    heapq.heappush(queue, (new_score, neighbor))

        return {
            "start": start,
            "scores": scores,
            "ap_costs": ap_costs,
            "penalties": penalties,
            "previous": previous,
            "previous_actions": previous_actions,
        }

    def reconstruct_plan(self, search, target):
        """Recover the executable action sequence for one Dijkstra destination."""
        if target not in search["scores"]:
            return None

        segments = []
        current = target

        while current != search["start"]:
            segments.append(search["previous_actions"][current])
            current = search["previous"][current]

        plan = []
        for segment in reversed(segments):
            plan.extend(segment)

        return plan

    def get_cleared_edges(self, plan, start):
        """Return doors opened and walls destroyed by a completed hypothetical route."""
        cleared_edges = set()
        current = start

        for kind, target in plan:
            if kind in ("open_door", "damage_wall"):
                cleared_edges.add(self.model.edge_key(current, target))
            elif kind == "move":
                current = target

        return cleared_edges

    def board_is_controlled(self):
        """A board is controlled while at most two RatKings are active."""
        rat_kings = sum(
            1 for entity in self.model.agents
            if isinstance(entity, RatKing) and entity.pos is not None
        )
        return rat_kings <= self.CONTROLLED_RAT_KING_LIMIT

    def get_task_bonus(self, kind):
        """Favor rescuing a revealed Patient while infestation is controlled."""
        if kind == "rescue" and self.board_is_controlled():
            return self.RESCUE_BONUS
        return 0

    def get_treatment_transition(self, position, infestation):
        """Return actions and cost needed to treat an infestation from one position."""
        if position != infestation.pos and not self.model.are_neighbors(position, infestation.pos):
            return None

        actions = []
        ap_cost = 0
        penalty = 0

        if position != infestation.pos:
            boundary = self.model.get_boundary(position, infestation.pos)

            if isinstance(boundary, Door) and not boundary.is_passable:
                actions.append(("open_door", infestation.pos))
                ap_cost += self.ACTION_COSTS["open_door"]

            elif isinstance(boundary, Wall) and not boundary.is_destroyed:
                hits = boundary.MAX_DAMAGE - boundary.damage
                actions.extend([("damage_wall", infestation.pos)] * hits)
                ap_cost += hits * self.ACTION_COSTS["damage_wall"]
                penalty += self.WALL_BREAK_PENALTY

        kind = "treat_rat_swarm" if isinstance(infestation, RatSwarm) else "treat_rat_king"
        actions.append((kind, infestation))
        ap_cost += self.ACTION_COSTS[kind]

        return {
            "score": ap_cost + penalty,
            "ap": ap_cost,
            "penalty": penalty,
            "actions": actions,
        }

    def get_claim_penalty(self, task):
        """Penalize targets already selected by other intelligent Doctors."""
        claimed_by_others = 0

        for doctor in self.model.doctors:
            if doctor is self or doctor.current_task is None:
                continue

            if not doctor.task_is_valid(doctor.current_task):
                continue

            if doctor.current_task["target"] is task["target"]:
                claimed_by_others += 1

        return claimed_by_others * self.TARGET_CLAIM_PENALTY

    def evaluate_task(self, task, normal_search=None):
        """Add Dijkstra cost, utility and an executable first-phase plan to a task."""
        kind = task["kind"]
        target = task["target"]

        if kind == "rescue_carried":
            search = self.dijkstra(self.pos, carrying=True)

            if self.model.is_exterior_position(self.pos):
                best_exit = self.pos
            else:
                reachable_exits = [position for position in self.model.EXTERIOR_ENTRANCES if position in search["scores"]]
                if not reachable_exits:
                    return None
                best_exit = min(reachable_exits, key=lambda position: search["scores"][position])

            plan = self.reconstruct_plan(search, best_exit) or []
            plan.append(("drop_patient", None))

            search_cost = search["scores"][best_exit]
            ap_cost = search["ap_costs"][best_exit]
            penalty = search["penalties"][best_exit]

        elif kind == "rescue":
            if target.pos is None:
                return None

            search = normal_search or self.dijkstra(self.pos)
            if target.pos not in search["scores"]:
                return None

            to_patient_plan = self.reconstruct_plan(search, target.pos)
            cleared_edges = self.get_cleared_edges(to_patient_plan, self.pos)
            carrying_search = self.dijkstra(target.pos, carrying=True, cleared_edges=cleared_edges)
            reachable_exits = [position for position in self.model.EXTERIOR_ENTRANCES if position in carrying_search["scores"]]

            if not reachable_exits:
                return None

            best_exit = min(reachable_exits, key=lambda position: carrying_search["scores"][position])

            search_cost = search["scores"][target.pos] + carrying_search["scores"][best_exit]
            ap_cost = search["ap_costs"][target.pos] + carrying_search["ap_costs"][best_exit]
            penalty = search["penalties"][target.pos] + carrying_search["penalties"][best_exit]

            # Execute only the route to the Patient now. Once picked up,
            # the next intelligent step recalculates the carrying route.
            plan = to_patient_plan + [("pick_up_patient", target)]

        elif kind == "investigate":
            if target.pos is None:
                return None

            search = normal_search or self.dijkstra(self.pos)
            if target.pos not in search["scores"]:
                return None

            search_cost = search["scores"][target.pos]
            ap_cost = search["ap_costs"][target.pos]
            penalty = search["penalties"][target.pos]
            plan = self.reconstruct_plan(search, target.pos)

            if not plan:
                return None

        elif kind in ("treat_rat_swarm", "treat_rat_king"):
            if target.pos is None:
                return None

            search = normal_search or self.dijkstra(self.pos)
            candidates = [self.pos] if self.pos == target.pos else []
            candidates += self.model.get_neighbors(target.pos)

            best = None

            for position in candidates:
                if position not in search["scores"]:
                    continue

                treatment = self.get_treatment_transition(position, target)
                if treatment is None:
                    continue

                total_score = search["scores"][position] + treatment["score"]

                if best is None or total_score < best["score"]:
                    best = {
                        "score": total_score,
                        "ap": search["ap_costs"][position] + treatment["ap"],
                        "penalty": search["penalties"][position] + treatment["penalty"],
                        "plan": (self.reconstruct_plan(search, position) or []) + treatment["actions"],
                    }

            if best is None:
                return None

            search_cost = best["score"]
            ap_cost = best["ap"]
            penalty = best["penalty"]
            plan = best["plan"]

        else:
            return None

        claim_penalty = self.get_claim_penalty(task)
        task_bonus = self.get_task_bonus(kind)
        effective_cost = search_cost + claim_penalty - task_bonus

        evaluated = dict(task)
        evaluated.update({
            "search_cost": search_cost,
            "ap_cost": ap_cost,
            "wall_penalty": penalty,
            "claim_penalty": claim_penalty,
            "task_bonus": task_bonus,
            "effective_cost": effective_cost,
            "utility": -effective_cost,
            "plan": plan,
        })
        return evaluated

    def choose_task(self):
        """Choose the task with the lowest Dijkstra weighted cost."""
        tasks = self.get_tasks()

        if not tasks:
            return None

        normal_search = None if self.carried_patient is not None else self.dijkstra(self.pos)
        evaluated = []

        for task in tasks:
            result = self.evaluate_task(task, normal_search)
            if result is not None:
                evaluated.append(result)

        if not evaluated:
            return None

        return max(
            evaluated,
            key=lambda task: (
                task["utility"],
                -getattr(task["target"], "unique_id", 0),
            ),
        )

    def task_is_valid(self, task):
        if task is None:
            return False

        if task["kind"] == "rescue_carried":
            return self.carried_patient is task["target"]

        return task["target"].pos is not None

    def step_intelligent(self):
        """Choose a coordinated low-cost task and execute one planned action."""
        if self.recalculate_task or not self.task_is_valid(self.current_task):
            self.current_task = self.choose_task()
            self.recalculate_task = False

        if self.current_task is None:
            self.end_turn()
            return False

        normal_search = None if self.carried_patient is not None else self.dijkstra(self.pos)
        evaluated = self.evaluate_task(self.current_task, normal_search)

        if evaluated is None or not evaluated["plan"]:
            self.current_task = self.choose_task()
            if self.current_task is None:
                self.end_turn()
                return False
            evaluated = self.current_task

        self.current_task = evaluated
        action = evaluated["plan"][0]

        # If the next planned action is currently too expensive,
        # keep the target reserved and continue it next turn.
        if action not in self.get_available_actions():
            self.end_turn()
            return False

        if not self.execute_action(action):
            self.current_task = None
            self.recalculate_task = True
            self.end_turn()
            return False

        if not self.task_is_valid(self.current_task):
            self.current_task = None
            self.recalculate_task = True

        return True

    # ==========================================================
    # STRATEGY DISPATCH
    # ==========================================================

    def step(self):
        if self.strategy == "skip":
            self.end_turn()
            return False

        if self.strategy == "random":
            return self.step_random()

        if self.strategy == "intelligent":
            return self.step_intelligent()

        raise ValueError(f"Unsupported Doctor strategy: {self.strategy}")
