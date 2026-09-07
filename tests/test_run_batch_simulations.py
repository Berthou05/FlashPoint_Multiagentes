from contextlib import redirect_stderr
from io import StringIO
import unittest

from run_batch_simulations import run_batch


class TestRunBatchSimulations(unittest.TestCase):
    def test_run_batch_returns_only_the_requested_summary(self):
        summary = run_batch(seed_start=1, games=2, max_turns=5, workers=1)

        self.assertEqual(summary["games"], 2)
        self.assertEqual(summary["seed_start"], 1)
        self.assertEqual(summary["seed_end"], 2)
        self.assertEqual(summary["successes"] + summary["failures"], 2)
        self.assertIn("average_turns_won", summary)
        self.assertIn("average_turns_lost", summary)
        self.assertIn("truncated_at_limit", summary)

    def test_run_batch_can_report_progress(self):
        output = StringIO()

        with redirect_stderr(output):
            run_batch(seed_start=1, games=2, max_turns=5, progress=True, workers=1)

        self.assertEqual(output.getvalue().splitlines(), ["Completed 1/2", "Completed 2/2"])

    def test_run_batch_can_use_multiple_workers(self):
        summary = run_batch(seed_start=1, games=2, max_turns=5, workers=2)

        self.assertEqual(summary["successes"] + summary["failures"], 2)


if __name__ == "__main__":
    unittest.main()
