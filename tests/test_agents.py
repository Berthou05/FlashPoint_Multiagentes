import unittest
from unittest.mock import patch

from plague_sim.entities import RatKing, RatSwarm
from plague_sim.model import PlagueSimulationModel


class TestPlagueDoctorActions(unittest.TestCase):
    """Pruebas de las acciones que todas las estrategias comparten."""

    def setUp(self):
        self.model = PlagueSimulationModel(seed=7)
        self.doctor = self.model.doctors[0]

    def test_open_door_then_move_pays_each_action_once(self):
        self.model.grid.move_agent(self.doctor, (2, 4))
        infestation = self.model.get_infestation_at((3, 4))
        self.model.remove_infestation(infestation)
        self.doctor.start_turn()

        self.assertFalse(self.doctor.move((3, 4)))
        self.assertEqual(self.doctor.action_points, 4)
        self.assertTrue(self.doctor.open_door((3, 4)))
        self.assertTrue(self.doctor.move((3, 4)))
        self.assertEqual(self.doctor.action_points, 2)

    def test_damage_wall_requires_two_paid_actions_before_crossing(self):
        self.model.grid.move_agent(self.doctor, (2, 3))
        self.doctor.start_turn()

        self.assertFalse(self.doctor.move((3, 3)))
        self.assertTrue(self.doctor.damage_wall((3, 3)))
        self.assertFalse(self.doctor.move((3, 3)))
        self.assertTrue(self.doctor.damage_wall((3, 3)))
        self.assertTrue(self.doctor.move((3, 3)))
        self.assertEqual(self.doctor.action_points, 1)

    def test_treats_a_neighboring_swarm_but_not_through_a_closed_door(self):
        self.model.grid.move_agent(self.doctor, (2, 4))
        infestation = self.model.get_infestation_at((3, 4))
        self.model.remove_infestation(infestation)
        swarm = self.model.create_rat_swarm((3, 4))
        self.doctor.start_turn()

        self.assertFalse(self.doctor.treat_rat_swarm(swarm.unique_id))
        self.assertEqual(self.doctor.action_points, 4)
        self.assertTrue(self.doctor.open_door((3, 4)))
        self.assertTrue(self.doctor.treat_rat_swarm(swarm.unique_id))
        self.assertIsNone(self.model.get_infestation_at((3, 4)))
        self.assertEqual(self.doctor.action_points, 2)

    def test_pick_up_drop_and_carrying_movement_preserve_patient_identity(self):
        self.model.grid.move_agent(self.doctor, (1, 1))
        patient = self.model.create_patient((1, 1))
        self.doctor.start_turn()

        self.assertTrue(self.doctor.pick_up_patient(patient.unique_id))
        self.assertIs(self.doctor.carried_patient, patient)
        self.assertIsNone(patient.pos)
        self.assertTrue(self.doctor.move((1, 2)))
        self.assertTrue(self.doctor.drop_patient())
        self.assertIs(self.model.get_patient_at((1, 2)), patient)
        self.assertIsNone(self.doctor.carried_patient)
        self.assertEqual(self.doctor.action_points, 0)

    def test_dropping_a_patient_outside_rescues_it(self):
        self.model.grid.move_agent(self.doctor, (4, 0))
        patient = self.model.create_patient((4, 0))
        self.doctor.start_turn()

        self.assertTrue(self.doctor.pick_up_patient(patient.unique_id))
        self.assertTrue(self.doctor.drop_patient())
        self.assertIsNone(self.doctor.carried_patient)
        self.assertNotIn(patient, self.model.agents)
        self.assertEqual(self.model.patients_rescued, 1)

    def test_rat_king_knocks_down_doctor_and_kills_carried_patient_once(self):
        self.model.grid.move_agent(self.doctor, (2, 2))
        patient = self.model.create_patient((2, 2))
        self.doctor.start_turn()
        self.assertTrue(self.doctor.pick_up_patient(patient.unique_id))

        self.model.create_rat_king((2, 2))

        self.assertIsNone(self.doctor.carried_patient)
        self.assertEqual(self.model.patients_killed, 1)
        self.assertNotEqual(self.doctor.pos, (2, 2))
        self.model.resolve_rat_king_cell((2, 2))
        self.assertEqual(self.model.patients_killed, 1)

    def test_random_step_executes_one_action_from_the_available_list(self):
        self.doctor.strategy = "random"
        self.doctor.start_turn()
        action = {"kind": "move", "target": (4, 1)}

        with patch.object(self.doctor, "get_available_actions", return_value=[action]):
            self.doctor.step()

        self.assertEqual(self.doctor.pos, (4, 1))
        self.assertEqual(self.doctor.action_points, 3)
        self.assertFalse(self.doctor.turn_completed)

    def test_random_model_completes_a_turn_without_progress_error(self):
        random_model = PlagueSimulationModel(strategy="random", seed=7)

        random_model.step_complete_turn()

        self.assertIn(random_model.phase, ("doctor", "finished"))
        self.assertGreaterEqual(random_model.turn, 0)


if __name__ == "__main__":
    unittest.main()
