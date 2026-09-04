import mesa

from .entities import Wall, Door


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
        Return the AP cost required to move from one neighboring
        cell to another.

        This method is also intended to be used by pathfinding.
        """

        boundary = self.model.get_boundary(current, target)

        # Normal movement.
        cost = self.get_action_cost("move")

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

            # Closed Door:
            # opening + moving through it.
            return (
                self.get_action_cost("open_door")
                + cost
            )

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
    # AGENT BEHAVIOUR
    # ========================================================

    def step(self):
        """
        Decide and perform one action.

        The temporary skip strategy ends immediately so the environment
        can be tested before decision logic is implemented.
        """
        if self.strategy == "skip":
            self.end_turn()
