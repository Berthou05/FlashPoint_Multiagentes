"""Simple entities used by the PlaguePoint simulation."""

from mesa import Agent


class Patient(Agent):
    """A revealed patient on the board or carried by a doctor."""

    def __init__(self, model):
        super().__init__(model)


class POI(Agent):
    """A hidden Point of Interest that may contain a patient."""

    def __init__(self, model, has_patient):
        super().__init__(model)
        self.has_patient = has_patient
        self.is_revealed = False

    def reveal(self):
        self.is_revealed = True
        return self.has_patient


class RatSwarm(Agent):
    """PlaguePoint equivalent of Smoke."""

    def __init__(self, model):
        super().__init__(model)


class RatKing(Agent):
    """PlaguePoint equivalent of Fire."""

    def __init__(self, model):
        super().__init__(model)


class Wall:
    """A wall between two cells. Two hits destroy it."""

    MAX_DAMAGE = 2

    def __init__(self):
        self.damage = 0
        self.is_destroyed = False

    @property
    def is_passable(self):
        return self.is_destroyed

    def take_damage(self):
        """Apply one damage and return new structural damage added."""
        if self.is_destroyed:
            return 0

        self.damage += 1

        if self.damage >= self.MAX_DAMAGE:
            self.damage = self.MAX_DAMAGE
            self.is_destroyed = True

        return 1


class Door:
    """A door between two cells. One damage action destroys it."""

    MAX_DAMAGE = 2

    def __init__(self, is_open=False):
        self.damage = 0
        self.is_open = is_open
        self.is_destroyed = False

    @property
    def is_passable(self):
        return self.is_open or self.is_destroyed

    def open(self):
        if not self.is_destroyed:
            self.is_open = True

    def close(self):
        if not self.is_destroyed:
            self.is_open = False

    def toggle(self):
        if self.is_destroyed:
            return False

        self.is_open = not self.is_open
        return True

    def take_damage(self):
        """Destroy the door without adding structural house damage."""
        if self.is_destroyed:
            return 0

        self.damage = self.MAX_DAMAGE
        self.is_destroyed = True
        self.is_open = True
        return 0
