import mesa

from .entities import Door, RatKing, RatSwarm, Wall


class PlagueDoctorAgent(mesa.Agent):

    # ========================================================
    # ACTION POINTS
    # ========================================================

    MAX_ACTION_POINTS = 4

    # Keep every fixed AP cost in one place.
    # Update these values once the final game rules are defined.
    ACTION_COSTS = {
        "move": 1,
        "open_door": 1,
        "close_door": 1,
        "damage_wall": 1,
        "treat_rat_swarm": 1,
        "treat_rat_king": 2,
        "pick_up_patient": 1,
        "drop_patient": 1,
        "move_carrying_patient": 2,
    }

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self, model, strategy="random"):
        super().__init__(model)

        self.strategy = strategy
        self.action_points = self.MAX_ACTION_POINTS

        # None means the Doctor is not carrying a Patient.
        # Otherwise this stores the actual Patient object.
        self.carried_patient = None

        self.turn_completed = False

    # ========================================================
    # ACTION POINT HELPERS
    # ========================================================

    def get_action_cost(self, action):
        """
        Return the AP cost of a fixed action.
        """
        return self.ACTION_COSTS[action]

    def can_afford(self, cost):
        """
        Check whether the Doctor has enough AP.
        """
        return self.action_points >= cost

    def spend_ap(self, cost):
        """
        Spend AP if enough points are available.

        Returns True if the cost was paid.
        Returns False otherwise.
        """
        if not self.can_afford(cost):
            return False

        self.action_points -= cost
        return True

    # ========================================================
    # MOVEMENT COST
    # ========================================================

    def get_transition_cost(self, current, target):
        """
        Return the cost of the immediate movement between two cells.

        Opening a closed door is a separate action.  Keeping that cost out
        of this method makes the route later produced by UCS executable as
        an explicit sequence of actions.
        """

        if not self.model.are_neighbors(current, target):
            return float("inf")

        boundary = self.model.get_boundary(current, target)

        # Carrying a Patient makes every movement action more expensive.
        cost_name = (
            "move_carrying_patient"
            if self.carried_patient is not None
            else "move"
        )
        cost = self.get_action_cost(cost_name)

        # No Wall or Door between the cells.
        if boundary is None:
            return cost

        # A destroyed Wall can be crossed.
        if isinstance(boundary, Wall):

            if boundary.is_passable:
                return cost

            # An intact Wall cannot be crossed as part of a
            # normal movement action.
            return float("inf")

        # Door movement depends on its state.
        if isinstance(boundary, Door):

            # Open or destroyed Door.
            if boundary.is_passable:
                return cost

            # A closed door must be opened before moving.
            return float("inf")

        return float("inf")

    # ========================================================
    # PATIENT STATE
    # ========================================================

    @property
    def is_carrying_patient(self):
        """
        True whenever this Doctor is carrying a Patient.
        """
        return self.carried_patient is not None

    # ========================================================
    # TURN MANAGEMENT
    # ========================================================

    def start_turn(self):
        """
        Reset the Doctor for a new turn.
        """
        self.action_points = self.MAX_ACTION_POINTS
        self.turn_completed = False

    def has_actions_remaining(self):
        """Return whether the Doctor can still act during its turn."""
        return self.action_points > 0 and not self.turn_completed

    def end_turn(self):
        """
        Mark the Doctor's turn as completed.
        """
        self.turn_completed = True

    # ========================================================
    # DOCTOR ACTIONS
    # ========================================================

    def move(self, target):
        """Move one cell when the model accepts the movement."""
        cost = self.get_transition_cost(self.pos, target)
        if cost == float("inf") or not self.model.is_action_legal(
            self, {"kind": "move", "target": target}
        ):
            return False
        if not self.spend_ap(cost):
            return False
        return self.model.move_doctor(self, target)

    def open_door(self, target):
        """Open the adjacent closed door and pay one AP."""
        action = {"kind": "open_door", "target": target}
        if not self.model.is_action_legal(self, action):
            return False
        if not self.spend_ap(self.get_action_cost("open_door")):
            return False
        return self.model.open_door(self.pos, target)

    def close_door(self, target):
        """Close the adjacent open door and pay one AP."""
        action = {"kind": "close_door", "target": target}
        if not self.model.is_action_legal(self, action):
            return False
        if not self.spend_ap(self.get_action_cost("close_door")):
            return False
        return self.model.close_door(self.pos, target)

    def damage_wall(self, target):
        """Damage an adjacent intact wall and pay one AP."""
        action = {"kind": "damage_wall", "target": target}
        if not self.model.is_action_legal(self, action):
            return False
        if not self.spend_ap(self.get_action_cost("damage_wall")):
            return False
        self.model.damage_boundary(self.pos, target)
        return True

    def _treat_infestation(self, target_id, action_name):
        """Remove one reachable infestation after paying its action cost."""
        action = {"kind": action_name, "target": target_id}
        if not self.model.is_action_legal(self, action):
            return False
        if not self.spend_ap(self.get_action_cost(action_name)):
            return False
        infestation = self.model.get_agent_by_id(target_id)
        self.model.remove_infestation(infestation)
        return True

    def treat_rat_swarm(self, target_id):
        """Treat a reachable RatSwarm."""
        return self._treat_infestation(target_id, "treat_rat_swarm")

    def treat_rat_king(self, target_id):
        """Treat a reachable RatKing."""
        return self._treat_infestation(target_id, "treat_rat_king")

    def pick_up_patient(self, target_id):
        """Pick up the Patient in the Doctor's current cell."""
        action = {"kind": "pick_up_patient", "target": target_id}
        if not self.model.is_action_legal(self, action):
            return False
        if not self.spend_ap(self.get_action_cost("pick_up_patient")):
            return False
        patient = self.model.get_agent_by_id(target_id)
        self.model.grid.remove_agent(patient)
        self.carried_patient = patient
        self.model.emit_event("patient_picked_up", id=patient.unique_id)
        return True

    def drop_patient(self):
        """Drop a carried Patient, or rescue it when outside the house."""
        if not self.model.is_action_legal(
            self, {"kind": "drop_patient", "target": None}
        ):
            return False
        if not self.spend_ap(self.get_action_cost("drop_patient")):
            return False

        patient = self.carried_patient
        if self.model.is_exterior_position(self.pos):
            self.model.rescue_patient(patient)
        else:
            self.model.grid.place_agent(patient, self.pos)
            self.carried_patient = None
            self.model.emit_event(
                "patient_dropped",
                id=patient.unique_id,
                position=list(self.pos),
            )
        return True

    def get_action_ap_cost(self, action):
        """Return the AP cost of one concrete action dictionary."""
        if action["kind"] == "move":
            return self.get_transition_cost(self.pos, action["target"])
        return self.get_action_cost(action["kind"])

    def get_available_actions(self):
        """Return every legal action the Doctor can still afford.

        The order is stable so a seed always reproduces the same random
        choices, even when Mesa changes an internal collection order.
        """
        actions = []

        for target in sorted(self.model.get_neighbors(self.pos)):
            actions.extend([
                {"kind": "move", "target": target},
                {"kind": "open_door", "target": target},
                {"kind": "close_door", "target": target},
                {"kind": "damage_wall", "target": target},
            ])

        for entity in sorted(self.model.agents, key=lambda item: item.unique_id):
            if isinstance(entity, RatSwarm):
                actions.append({"kind": "treat_rat_swarm", "target": entity.unique_id})
            elif isinstance(entity, RatKing):
                actions.append({"kind": "treat_rat_king", "target": entity.unique_id})

        patient = self.model.get_patient_at(self.pos)
        if patient is not None:
            actions.append({"kind": "pick_up_patient", "target": patient.unique_id})
        actions.append({"kind": "drop_patient", "target": None})

        return [
            action
            for action in actions
            if self.model.is_action_legal(self, action)
            and self.can_afford(self.get_action_ap_cost(action))
        ]

    def execute_action(self, action):
        """Dispatch one already selected action to its concrete method."""
        kind = action["kind"]
        target = action["target"]
        if kind == "move":
            return self.move(target)
        if kind == "open_door":
            return self.open_door(target)
        if kind == "close_door":
            return self.close_door(target)
        if kind == "damage_wall":
            return self.damage_wall(target)
        if kind == "treat_rat_swarm":
            return self.treat_rat_swarm(target)
        if kind == "treat_rat_king":
            return self.treat_rat_king(target)
        if kind == "pick_up_patient":
            return self.pick_up_patient(target)
        if kind == "drop_patient":
            return self.drop_patient()
        return False

    # ========================================================
    # AGENT BEHAVIOUR
    # ========================================================

    def step(self):
        """
        Decide and perform one action.

        Skip ends immediately. Random chooses exactly one legal action.
        """
        if self.strategy == "skip":
            self.end_turn()
            return

        if self.strategy == "random":
            actions = self.get_available_actions()
            if not actions:
                self.end_turn()
                return

            action = self.model.random.choice(actions)
            if not self.execute_action(action):
                raise RuntimeError("A selected legal Doctor action could not execute.")
            return

        raise ValueError(f"Unsupported Doctor strategy: {self.strategy}")
