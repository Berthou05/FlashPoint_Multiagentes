import unittest
from unittest.mock import patch

from plague_sim.entities import Patient, RatKing, RatSwarm
from plague_sim.model import PlagueSimulationModel


class TestPlagueDoctorActions(unittest.TestCase):
    """Pruebas de las acciones que todas las estrategias comparten."""

    def setUp(self):
        self.model = PlagueSimulationModel(seed=7)
        self.doctor = self.model.doctors[0]

    def action(self, kind, target=None):
        return self.doctor.execute_action((kind, target))

    def test_open_door_then_move_pays_each_action_once(self):
        self.model.grid.move_agent(self.doctor, (4, 5))
        infestation = next(
            entity
            for entity in self.model.grid.get_cell_list_contents([(4, 4)])
            if isinstance(entity, RatKing)
        )
        self.model.remove_infestation(infestation)
        self.doctor.start_turn()

        self.assertFalse(self.action("move", (4, 4)))
        self.assertEqual(self.doctor.action_points, 4)
        self.assertTrue(self.action("open_door", (4, 4)))
        self.assertTrue(self.action("move", (4, 4)))
        self.assertEqual(self.doctor.action_points, 2)

    def test_damage_wall_requires_two_paid_actions_before_crossing(self):
        self.model.grid.move_agent(self.doctor, (3, 5))
        self.doctor.start_turn()
        self.doctor.action_points = 6

        self.assertFalse(self.action("move", (3, 4)))
        self.assertTrue(self.action("damage_wall", (3, 4)))
        self.assertFalse(self.action("move", (3, 4)))
        self.assertTrue(self.action("damage_wall", (3, 4)))
        self.assertTrue(self.action("move", (3, 4)))
        self.assertEqual(self.doctor.action_points, 1)

    def test_treats_a_neighboring_swarm_but_not_through_a_closed_door(self):
        self.model.grid.move_agent(self.doctor, (4, 5))
        infestation = next(
            entity
            for entity in self.model.grid.get_cell_list_contents([(4, 4)])
            if isinstance(entity, RatKing)
        )
        self.model.remove_infestation(infestation)
        swarm = self.model.create_rat_swarm((4, 4))
        self.doctor.start_turn()

        self.assertNotIn(
            ("treat_rat_swarm", swarm),
            self.doctor.get_available_actions(),
        )
        self.assertEqual(self.doctor.action_points, 4)
        self.assertTrue(self.action("open_door", (4, 4)))
        self.assertTrue(self.action("treat_rat_swarm", swarm))
        self.assertFalse(any(
            isinstance(entity, (RatSwarm, RatKing))
            for entity in self.model.grid.get_cell_list_contents([(4, 4)])
        ))
        self.assertEqual(self.doctor.action_points, 2)

    def test_pick_up_drop_and_carrying_movement_preserve_patient_identity(self):
        self.model.grid.move_agent(self.doctor, (1, 1))
        patient = self.model.create_patient((1, 1))
        self.doctor.start_turn()

        self.assertTrue(self.action("pick_up_patient", patient))
        self.assertIs(self.doctor.carried_patient, patient)
        self.assertIsNone(patient.pos)
        self.assertTrue(self.action("move", (1, 2)))
        self.assertTrue(self.action("drop_patient"))
        self.assertIn(
            patient,
            self.model.grid.get_cell_list_contents([(1, 2)]),
        )
        self.assertIsNone(self.doctor.carried_patient)
        self.assertEqual(self.doctor.action_points, 2)

    def test_dropping_a_patient_outside_rescues_it(self):
        self.model.grid.move_agent(self.doctor, (0, 3))
        patient = self.model.create_patient((0, 3))
        self.doctor.start_turn()

        self.assertTrue(self.action("pick_up_patient", patient))
        self.assertTrue(self.action("drop_patient"))
        self.assertIsNone(self.doctor.carried_patient)
        self.assertNotIn(patient, self.model.agents)
        self.assertEqual(self.model.patients_rescued, 1)

    def test_rat_king_knocks_down_doctor_and_kills_carried_patient_once(self):
        self.model.grid.move_agent(self.doctor, (2, 2))
        patient = self.model.create_patient((2, 2))
        self.doctor.start_turn()
        self.assertTrue(self.action("pick_up_patient", patient))

        self.model.create_rat_king((2, 2))

        self.assertIsNone(self.doctor.carried_patient)
        self.assertEqual(self.model.patients_killed, 1)
        self.assertNotEqual(self.doctor.pos, (2, 2))
        self.model.resolve_rat_king_cell((2, 2))
        self.assertEqual(self.model.patients_killed, 1)

    def test_random_step_executes_one_action_from_the_available_list(self):
        self.doctor.strategy = "random"
        self.doctor.start_turn()
        action = ("move", (1, 3))

        with patch.object(self.doctor, "get_available_actions", return_value=[action]):
            self.assertTrue(self.doctor.step())

        self.assertEqual(self.doctor.pos, (1, 3))
        self.assertEqual(self.doctor.action_points, 3)
        self.assertFalse(self.doctor.turn_completed)

    def test_action_points_start_empty_and_accumulate_up_to_eight(self):
        self.assertEqual(self.doctor.action_points, 0)

        self.doctor.start_turn()
        self.assertEqual(self.doctor.action_points, 4)

        self.doctor.action_points = 2
        self.doctor.start_turn()
        self.assertEqual(self.doctor.action_points, 6)

        self.doctor.action_points = 6
        self.doctor.start_turn()
        self.assertEqual(self.doctor.action_points, 8)

    def test_free_pickup_and_rescue_work_when_no_action_points_remain(self):
        self.model.grid.move_agent(self.doctor, (0, 3))
        patient = self.model.create_patient((0, 3))
        self.doctor.action_points = 0

        self.assertTrue(self.action("pick_up_patient", patient))
        self.assertTrue(self.action("drop_patient"))
        self.assertIsNone(self.doctor.carried_patient)
        self.assertEqual(self.model.patients_rescued, 1)

    def test_random_does_not_offer_free_drop_inside_the_house(self):
        self.model.grid.move_agent(self.doctor, (1, 1))
        patient = self.model.create_patient((1, 1))
        self.doctor.action_points = 0
        self.assertTrue(self.action("pick_up_patient", patient))

        actions = self.doctor.get_available_actions()

        self.assertNotIn(("drop_patient", None), actions)

    def test_intelligent_doctor_carrying_patient_only_considers_nearby_rat_kings(self):
        self.doctor.strategy = "intelligent"
        self.model.grid.move_agent(self.doctor, (1, 1))
        patient = self.model.create_patient((1, 1))
        self.doctor.start_turn()
        self.assertTrue(self.action("pick_up_patient", patient))

        rat_king = self.model.create_rat_king((1, 2))
        swarm = self.model.create_rat_swarm((2, 1))

        tasks = self.doctor.get_tasks()

        self.assertEqual(
            {(task["kind"], task["target"]) for task in tasks},
            {
                ("rescue_carried", patient),
                ("treat_rat_king", rat_king),
            },
        )
        self.assertNotIn(
            ("treat_rat_swarm", swarm),
            {(task["kind"], task["target"]) for task in tasks},
        )

    def test_intelligent_doctor_saves_four_action_points_for_an_unfinished_rescue(self):
        self.doctor.strategy = "intelligent"
        self.model.grid.move_agent(self.doctor, (1, 1))
        patient = self.model.create_patient((8, 6))
        self.doctor.action_points = 4
        self.doctor.current_task = {"kind": "rescue", "target": patient}
        self.doctor.recalculate_task = False

        self.assertFalse(self.doctor.step_intelligent())

        self.assertTrue(self.doctor.turn_completed)
        self.assertEqual(self.doctor.action_points, 4)
        self.assertEqual(self.doctor.pos, (1, 1))

    def test_skip_step_reports_turn_end(self):
        self.doctor.strategy = "skip"

        self.assertIs(self.doctor.step(), False)
        self.assertTrue(self.doctor.turn_completed)

    def test_available_actions_use_objects_and_include_all_patients_in_cell(self):
        self.model.grid.move_agent(self.doctor, (1, 1))
        first_patient = self.model.create_patient((1, 1))
        second_patient = self.model.create_patient((1, 1))
        swarm = self.model.create_rat_swarm((1, 2))
        self.doctor.start_turn()

        actions = self.doctor.get_available_actions()

        self.assertIn(("pick_up_patient", first_patient), actions)
        self.assertIn(("pick_up_patient", second_patient), actions)
        self.assertIn(("treat_rat_swarm", swarm), actions)
        self.assertNotIn(("move", (0, 1)), actions)

    def test_execute_action_changes_door_and_pays_once(self):
        self.model.grid.move_agent(self.doctor, (4, 5))
        self.doctor.start_turn()
        door = self.model.get_boundary((4, 5), (4, 4))

        self.assertTrue(self.action("open_door", (4, 4)))

        self.assertTrue(door.is_open)
        self.assertEqual(self.doctor.action_points, 3)

    def test_open_door_event_identifies_the_boundary_for_unity(self):
        self.model.grid.move_agent(self.doctor, (4, 5))
        self.doctor.start_turn()
        self.model.events = []

        self.assertTrue(self.action("open_door", (4, 4)))

        self.assertEqual(self.model.events[0], {
            "sequence": 1,
            "type": "door_opened",
            "id": self.model.get_boundary_id((4, 5), (4, 4)),
            "ax": 4,
            "ay": 4,
            "bx": 4,
            "by": 5,
            "open": True,
        })

    def test_action_event_reports_remaining_action_points(self):
        self.model.grid.move_agent(self.doctor, (4, 5))
        self.doctor.start_turn()
        self.model.events = []

        self.assertTrue(self.action("open_door", (4, 4)))

        self.assertEqual(self.model.events[-1], {
            "sequence": 2,
            "type": "doctor_action_completed",
            "doctor_id": self.doctor.unique_id,
            "action_points_after": 3,
        })

    def test_random_model_completes_a_turn_without_progress_error(self):
        random_model = PlagueSimulationModel(strategy="random", seed=7)

        random_model.step_complete_turn()

        self.assertIn(random_model.phase, ("doctor", "finished"))
        self.assertGreaterEqual(random_model.turn, 0)


if __name__ == "__main__":
    unittest.main()
