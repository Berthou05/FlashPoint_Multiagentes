import mesa

from .entities import Door, POI, Patient, RatKing, RatSwarm, Wall


class PlagueDoctorAgent(mesa.Agent):
    """Doctor that decides and executes actions on the shared board."""

    MAX_ACTION_POINTS = 8

    ACTION_COSTS = {
        "move": 1,
        "open_door": 1,
        "close_door": 1,
        "damage_wall": 2,
        "treat_rat_swarm": 1,
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

    def spend_ap(self, cost):
        if self.action_points < cost:
            return False
        self.action_points -= cost
        return True

    def get_transition_cost(self, current, target):
        """AP cost for pathfinding across one neighboring edge."""
        if not self.model.are_neighbors(current, target):
            return float("inf")

        move_cost = self.ACTION_COSTS[
            "move_carrying_patient" if self.carried_patient is not None else "move"
        ]
        boundary = self.model.get_boundary(current, target)

        if boundary is None or boundary.is_passable:
            return move_cost
        if isinstance(boundary, Door):
            return self.ACTION_COSTS["open_door"] + move_cost
        return float("inf")

    def start_turn(self):
        self.action_points = min(self.action_points + 4, self.MAX_ACTION_POINTS)
        self.turn_completed = False

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
            if infestation is not None:
                kind = "treat_rat_swarm" if isinstance(infestation, RatSwarm) else "treat_rat_king"
                actions.append((kind, infestation))

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
        can_drop_carried_patient = (
            kind == "drop_patient"
            and target is None
            and self.carried_patient is not None
        )
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

    def step(self):
        if self.strategy == "skip":
            self.end_turn()
            return False

        if self.strategy == "random":
            actions = self.get_available_actions()
            if not actions:
                self.end_turn()
                return False

            if not self.execute_action(self.model.random.choice(actions)):
                raise RuntimeError("A selected legal Doctor action could not execute.")
            return True

        raise ValueError(f"Unsupported Doctor strategy: {self.strategy}")
