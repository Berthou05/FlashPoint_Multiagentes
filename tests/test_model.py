import unittest

from plague_sim.entities import Door, RatKing, RatSwarm, Wall
from plague_sim.model import PlagueSimulationModel


class TestPlagueSimulationModel(unittest.TestCase):
    def setUp(self):
        self.model = PlagueSimulationModel(seed=7)

    def test_house_keeps_doors_and_destroyed_walls_as_boundaries(self):
        wall = self.model.get_boundary((2, 3), (3, 3))
        door = self.model.get_boundary((2, 4), (3, 4))

        self.assertIsInstance(wall, Wall)
        self.assertIsInstance(door, Door)
        self.assertFalse(self.model.can_cross((2, 3), (3, 3)))
        self.assertEqual(self.model.damage_boundary((2, 3), (3, 3)), 1)
        self.assertEqual(self.model.damage_boundary((2, 3), (3, 3)), 1)
        self.assertIs(self.model.get_boundary((2, 3), (3, 3)), wall)
        self.assertTrue(self.model.can_cross((2, 3), (3, 3)))
        self.assertEqual(self.model.house_damage, 2)

    def test_infestation_progresses_from_swarm_to_king_to_outbreak(self):
        position = (2, 2)

        self.model.add_infestation(position)
        self.assertIsInstance(self.model.get_infestation_at(position), RatSwarm)

        self.model.add_infestation(position)
        self.assertIsInstance(self.model.get_infestation_at(position), RatKing)

        self.model.add_infestation(position)
        self.assertGreaterEqual(len(self.model.get_cell_contents((1, 2))), 1)

    def test_poi_reveal_creates_a_patient_in_the_same_cell(self):
        poi = self.model.create_poi((2, 2), True)

        patient = self.model.reveal_poi(poi)

        self.assertIsNotNone(patient)
        self.assertEqual(patient.pos, (2, 2))
        self.assertIsNone(self.model.get_poi_at((2, 2)))
        self.assertIs(self.model.get_patient_at((2, 2)), patient)

    def test_new_poi_removes_existing_infestation(self):
        position = (2, 2)
        self.model.add_infestation(position)

        poi = self.model.place_poi(position)

        self.assertIsNotNone(poi)
        self.assertIsNone(self.model.get_infestation_at(position))
        self.assertIs(self.model.get_poi_at(position), poi)

    def test_rat_king_kills_revealed_patient(self):
        position = (2, 2)
        patient = self.model.create_patient(position)

        self.model.create_rat_king(position)

        self.assertIsNone(self.model.get_patient_at(position))
        self.assertEqual(self.model.patients_killed, 1)
        self.assertNotIn(patient, self.model.agents)

    def test_rescuing_enough_patients_wins_the_game(self):
        for index in range(7):
            patient = self.model.create_patient((1 + (index % 6), 1))
            self.model.rescue_patient(patient)

        self.assertTrue(self.model.game_over)
        self.assertTrue(self.model.game_won)
        self.assertFalse(self.model.running)


if __name__ == "__main__":
    unittest.main()
