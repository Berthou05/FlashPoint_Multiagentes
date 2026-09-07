import unittest

from plague_sim.entities import Door, POI, Patient, RatKing, RatSwarm, Wall
from plague_sim.model import PlagueSimulationModel
from server import build_state


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
        self.assertIs(
            self.model.doctors[self.model.active_doctor_index],
            second_doctor,
        )

    def test_reset_starts_doctor_phase_without_events(self):
        self.assertEqual(self.model.phase, "doctor")
        self.assertFalse(self.model.doctor_turn_started)
        self.assertEqual(self.model.turn, 0)
        self.assertEqual(self.model.events, [])

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
        state = build_state(self.model)

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
        state = build_state(self.model)

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
        self.assertTrue(any(
            isinstance(entity, RatSwarm)
            for entity in self.model.grid.get_cell_list_contents([position])
        ))

        self.model.add_infestation(position)
        self.assertTrue(any(
            isinstance(entity, RatKing)
            for entity in self.model.grid.get_cell_list_contents([position])
        ))

        self.model.add_infestation(position)
        self.assertGreaterEqual(
            len(self.model.grid.get_cell_list_contents([(1, 2)])),
            1,
        )

    def test_poi_reveal_creates_a_patient_in_the_same_cell(self):
        poi = self.model.create_poi((2, 2), True)

        patient = self.model.reveal_poi(poi)

        self.assertIsNotNone(patient)
        self.assertEqual(patient.pos, (2, 2))
        contents = self.model.grid.get_cell_list_contents([(2, 2)])
        self.assertFalse(any(isinstance(entity, POI) for entity in contents))
        self.assertIn(patient, contents)

    def test_new_poi_removes_existing_infestation(self):
        position = (2, 2)
        self.model.add_infestation(position)

        poi = self.model.place_poi(position)

        self.assertIsNotNone(poi)
        contents = self.model.grid.get_cell_list_contents([position])
        self.assertFalse(any(
            isinstance(entity, (RatSwarm, RatKing)) for entity in contents
        ))
        self.assertIn(poi, contents)

    def test_rat_king_kills_revealed_patient(self):
        position = (2, 2)
        patient = self.model.create_patient(position)

        self.model.create_rat_king(position)

        self.assertFalse(any(
            isinstance(entity, Patient)
            for entity in self.model.grid.get_cell_list_contents([position])
        ))
        self.assertEqual(self.model.patients_killed, 1)
        self.assertNotIn(patient, self.model.agents)

    def test_rescuing_enough_patients_wins_the_game(self):
        for index in range(7):
            patient = self.model.create_patient((1 + (index % 6), 1))
            self.model.rescue_patient(patient)

        self.assertTrue(self.model.game_over)
        self.assertTrue(self.model.game_won)
        self.assertFalse(self.model.running)

    def test_statistics_preserve_patient_counts_when_house_collapses(self):
        patient = self.model.create_patient((1, 1))
        self.model.house_damage = 23

        self.model.damage_boundary((2, 3), (3, 3))

        statistics = self.model.get_statistics()
        self.assertTrue(self.model.game_over)
        self.assertEqual(statistics["end_reason"], "collapse")
        self.assertEqual(statistics["patients_killed"], 0)
        self.assertEqual(statistics["patients_on_board"], 1)
        self.assertEqual(patient.pos, (1, 1))

    def test_doctor_turns_started_counts_terminal_doctor_turn(self):
        random_model = PlagueSimulationModel(strategy="random", seed=7)

        random_model.step_doctor()

        self.assertEqual(random_model.doctor_turns_started, 1)
        self.assertEqual(random_model.get_statistics()["strategy"], "random")

    def test_model_does_not_own_unity_snapshot_serialization(self):
        self.assertFalse(hasattr(self.model, "get_state"))

    def test_model_does_not_keep_trivial_query_or_turn_helpers(self):
        removed_helpers = (
            "clear_events",
            "get_events",
            "get_cell_contents",
            "get_entities_at",
            "get_infestation_at",
            "get_poi_at",
            "get_patient_at",
            "get_patients_at",
            "get_doctors_at",
            "place_doctor",
            "get_active_doctor",
            "advance_active_doctor",
        )

        for helper in removed_helpers:
            self.assertFalse(hasattr(self.model, helper), helper)

    def test_build_state_matches_model_snapshot_contract(self):
        state = build_state(self.model)

        self.assertEqual(state["width"], self.model.width)
        self.assertEqual(state["height"], self.model.height)
        self.assertEqual(state["phase"], "doctor")
        self.assertEqual(len(state["doctors"]), 1)
        self.assertEqual(set(state["doctors"][0]), {
            "id",
            "x",
            "y",
            "action_points",
            "carried_patient_id",
        })


if __name__ == "__main__":
    unittest.main()
