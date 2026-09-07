import sys
import unittest
from unittest.mock import patch

from run_simulation import parse_arguments


class TestRunSimulation(unittest.TestCase):
    def test_parse_arguments_accepts_random_strategy(self):
        with patch.object(sys, "argv", ["run_simulation.py", "--strategy", "random"]):
            arguments = parse_arguments()

        self.assertEqual(arguments.strategy, "random")


if __name__ == "__main__":
    unittest.main()
