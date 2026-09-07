"""Run many simulations and print one summary of their final results."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import sys

from run_simulation import run_game


def run_batch(
    strategy="intelligent",
    num_agents=4,
    max_turns=500,
    games=100,
    seed_start=1,
    progress=False,
    workers=None,
):
    """Run consecutive seeds and return aggregate outcome statistics."""
    won_turns = []
    lost_turns = []
    successes = 0
    truncated_at_limit = 0

    with ProcessPoolExecutor(max_workers=workers) as executor:
        simulations = [
            executor.submit(run_game, strategy, num_agents, seed, max_turns)
            for seed in range(seed_start, seed_start + games)
        ]

        for completed, simulation in enumerate(as_completed(simulations), start=1):
            result = simulation.result()

            if result["result"] == "victory":
                successes += 1
                won_turns.append(result["turns_completed"])
            else:
                lost_turns.append(result["turns_completed"])

            if result["truncated"]:
                truncated_at_limit += 1

            if progress:
                print(f"Completed {completed}/{games}", file=sys.stderr)

    return {
        "strategy": strategy,
        "num_agents": num_agents,
        "games": games,
        "seed_start": seed_start,
        "seed_end": seed_start + games - 1,
        "successes": successes,
        "failures": games - successes,
        "average_turns_won": sum(won_turns) / len(won_turns) if won_turns else None,
        "average_turns_lost": sum(lost_turns) / len(lost_turns) if lost_turns else None,
        "truncated_at_limit": truncated_at_limit,
    }

    
def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", default="intelligent")
    parser.add_argument("--num-agents", type=int, default=4)
    parser.add_argument("--max-turns", type=int, default=500)
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--workers", type=int, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    print(json.dumps(
        run_batch(
            strategy=arguments.strategy,
            num_agents=arguments.num_agents,
            max_turns=arguments.max_turns,
            games=arguments.games,
            seed_start=arguments.seed_start,
            progress=arguments.progress,
            workers=arguments.workers,
        ),
        indent=2,
        sort_keys=True,
    ))
