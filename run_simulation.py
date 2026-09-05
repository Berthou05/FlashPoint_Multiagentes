"""Run one PlaguePoint game from the terminal and print its statistics."""

import argparse
import json

from plague_sim.model import PlagueSimulationModel


def run_game(strategy="random", num_agents=1, seed=None, max_turns=500):
    """Run complete turns until the game ends or the chosen limit is reached."""
    model = PlagueSimulationModel(strategy=strategy, num_agents=num_agents, seed=seed)

    while not model.game_over and model.doctor_turns_started < max_turns:
        model.step_complete_turn()

    statistics = model.get_statistics()
    statistics["truncated"] = not model.game_over
    statistics["max_turns"] = max_turns
    return statistics


def parse_arguments():
    """Read the small set of options needed for a reproducible run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strategy",
        choices=PlagueSimulationModel.SUPPORTED_STRATEGIES,
        default="random",
    )
    parser.add_argument("--num-agents", type=int, default=1)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--max-turns", type=int, default=500)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    print(json.dumps(
        run_game(
            strategy=arguments.strategy,
            num_agents=arguments.num_agents,
            seed=arguments.seed,
            max_turns=arguments.max_turns,
        ),
        indent=2,
        sort_keys=True,
    ))
