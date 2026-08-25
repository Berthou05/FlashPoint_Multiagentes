class Patient:
    def __init__(self, position):
        self.position = position
        self.is_carried = False

class POI:
    def __init__(self, position, content):
        self.position = position
        self.content = content
        self.is_revealed = False

class RatSwarm:
    def __init__(self, position):
        self.position = position

class RatKing:
    def __init__(self, position):
        self.position = position


# Structural elements of the environment

# Walls 
class Wall:
    def __init__(self, first_cell, second_cell):
        self.cells = tuple(sorted((first_cell, second_cell)))
        self.damage = 0
        self.is_destroyed = False

    def take_damage(self, amount=1):
        if self.is_destroyed:
            return

        self.damage += amount

        if self.damage >= 2:
            self.damage = 2
            self.is_destroyed = True

class Door:
    def __init__(self, first_cell, second_cell, is_open=False):
        self.cells = tuple(sorted((first_cell, second_cell)))
        self.damage = 0
        self.is_open = is_open
        self.is_destroyed = False