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

    def test_model_starts_one_skip_doctor_at_an_exterior_door(self):
        expected_positions = [(4, 0)]

        self.assertEqual(len(self.model.doctors), 1)
        self.assertEqual(
            [doctor.pos for doctor in self.model.doctors],
            expected_positions,
        )
        self.assertEqual(
            [doctor.strategy for doctor in self.model.doctors],
            ["skip"],
        )

    def test_skip_doctor_completes_turn_and_advances_to_next_doctor(self):
        self.model = PlagueSimulationModel(seed=7, num_agents=2)
        first_doctor = self.model.doctors[0]
        second_doctor = self.model.doctors[1]

        self.model.step()

        self.assertEqual(self.model.turn, 1)
        self.assertTrue(first_doctor.turn_completed)
        self.assertIs(self.model.get_active_doctor(), second_doctor)

    def test_reset_starts_doctor_phase_without_events(self):
        self.assertEqual(self.model.phase, "doctor")
        self.assertFalse(self.model.doctor_turn_started)
        self.assertEqual(self.model.turn, 0)
        self.assertEqual(self.model.get_events(), [])

    def test_step_doctor_completes_doctor_turn_and_enters_environment_phase(self):
        events = self.model.step_doctor()

        self.assertEqual(self.model.turn, 0)
        self.assertEqual(self.model.phase, "environment")
        self.assertEqual([event["sequence"] for event in events], [1, 2])
        self.assertEqual(
            [event["type"] for event in events],
            ["doctor_turn_started", "doctor_turn_ended"],
        )

    def test_doctor_action_points_are_integers_in_state(self):
        state = self.model.get_state()

        self.assertTrue(all(
            isinstance(doctor["action_points"], int)
            for doctor in state["doctors"]
        ))

    def test_step_environment_finishes_turn_and_returns_to_doctor_phase(self):
        self.model.step_doctor()

        events = self.model.step_environment()

        self.assertEqual(self.model.turn, 1)
        self.assertEqual(self.model.phase, "doctor")
        self.assertFalse(self.model.doctor_turn_started)
        self.assertEqual(events[0]["type"], "environment_started")
        self.assertEqual(events[-1]["type"], "environment_ended")
        self.assertEqual(
            [event["sequence"] for event in events],
            list(range(1, len(events) + 1)),
        )

    def test_step_environment_requires_environment_phase(self):
        with self.assertRaises(ValueError):
            self.model.step_environment()

    def test_complete_turn_combines_doctor_and_environment_events(self):
        events = self.model.step_complete_turn()

        self.assertEqual(self.model.turn, 1)
        self.assertEqual(self.model.phase, "doctor")
        self.assertEqual(events[0]["type"], "doctor_turn_started")
        self.assertIn("environment_started", [event["type"] for event in events])
        self.assertEqual(
            [event["sequence"] for event in events],
            list(range(1, len(events) + 1)),
        )

    def test_state_uses_unity_contract_fields_without_null_values(self):
        state = self.model.get_state()

        self.assertEqual(state["phase"], "doctor")
        self.assertEqual(state["game_status"], "running")
        self.assertNotIn("game_won", state)
        self.assertTrue(all(isinstance(item, dict) for item in state["rat_kings"]))
        self.assertEqual(set(state["doctors"][0]), {
            "id",
            "x",
            "y",
            "action_points",
            "carried_patient_id",
        })
        self.assertGreaterEqual(state["active_doctor_id"], 0)
        self.assertEqual(set(state["walls"][0]), {
            "id",
            "ax",
            "ay",
            "bx",
            "by",
            "damage",
            "destroyed",
        })
        self.assertEqual(set(state["doors"][0]), {
            "id",
            "ax",
            "ay",
            "bx",
            "by",
            "open",
            "destroyed",
        })

    def test_doctor_events_use_unity_field_names(self):
        events = self.model.step_doctor()

        self.assertEqual(events[0], {
            "sequence": 1,
            "type": "doctor_turn_started",
            "id": self.model.doctors[0].unique_id,
            "action_points": 4,
        })
        self.assertEqual(events[-1], {
            "sequence": 2,
            "type": "doctor_turn_ended",
            "id": self.model.doctors[0].unique_id,
            "action_points": 4,
        })

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
