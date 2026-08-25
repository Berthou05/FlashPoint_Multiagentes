"""Plague doctor agent declaration."""


class PlagueDoctorAgent:
    def __init__(self, unique_id, model):
        pass

    def step(self):
        pass

    def move(self, destination):
        pass

    def get_movement_cost(self, destination):
        pass

    def treat_infestation(self, position=None):
        pass

    def break_wall(self, wall):
        pass

    def open_close_door(self, door):
        pass

    def carry_patient(self, patient):
        pass

    def reveal_encounter(self, encounter):
        pass

    def evacuate_patient(self):
        pass

    def start_new_turn(self):
        pass

    def has_actions_remaining(self):
        pass

    def spend_action_points(self, amount):
        pass

    def end_turn(self):
        pass
