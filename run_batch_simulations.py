"""Run many simulations and print one summary of their final results."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import sys

from run_simulation import run_game


def average(values):
    return sum(values) / len(values) if values else None


def run_batch(
    strategy="intelligent",
    num_agents=6,
    max_turns=500,
    games=100,
    seed_start=1,
    progress=False,
    workers=None,
):
    """Run consecutive seeds and return aggregate outcome statistics."""
    wins = []
    losses = []
    collapses = []
    patient_losses = []
    truncated = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        simulations = {
            executor.submit(run_game, strategy, num_agents, seed, max_turns): seed
            for seed in range(seed_start, seed_start + games)
        }

        for completed, simulation in enumerate(as_completed(simulations), start=1):
            seed = simulations[simulation]
            result = simulation.result()
            result["seed"] = seed

            if result["result"] == "victory":
                wins.append(result)
            else:
                losses.append(result)

                if result.get("end_reason") == "collapse":
                    collapses.append(result)
                elif result.get("end_reason") == "patients_killed_4":
                    patient_losses.append(result)

            if result.get("truncated"):
                truncated.append(result)

            if progress:
                print(f"Completed {completed}/{games}", file=sys.stderr)

    def avg(results, key):
        return average([result[key] for result in results])

    failures = len(losses)

    return {
        "strategy": strategy,
        "num_agents": num_agents,
        "games": games,
        "seed_start": seed_start,
        "seed_end": seed_start + games - 1,

        "successes": len(wins),
        "failures": failures,
        "win_rate": len(wins) / games,

        "losses_by_collapse": len(collapses),
        "losses_by_patients": len(patient_losses),
        "truncated_at_limit": len(truncated),

        "collapse_rate_all_games": len(collapses) / games,
        "patient_loss_rate_all_games": len(patient_losses) / games,
        "truncated_rate_all_games": len(truncated) / games,

        "collapse_share_of_failures": len(collapses) / failures if failures else 0,
        "patient_loss_share_of_failures": len(patient_losses) / failures if failures else 0,
        "truncated_share_of_failures": len(truncated) / failures if failures else 0,

        "average_turns_won": avg(wins, "turns_completed"),
        "average_turns_lost": avg(losses, "turns_completed"),

        "average_patients_rescued": avg(wins + losses, "patients_rescued"),
        "average_patients_killed": avg(wins + losses, "patients_killed"),
        "average_house_damage": avg(wins + losses, "house_damage"),

        "average_patients_rescued_won": avg(wins, "patients_rescued"),
        "average_patients_killed_won": avg(wins, "patients_killed"),
        "average_house_damage_won": avg(wins, "house_damage"),

        "average_patients_rescued_lost": avg(losses, "patients_rescued"),
        "average_patients_killed_lost": avg(losses, "patients_killed"),
        "average_house_damage_lost": avg(losses, "house_damage"),

        "average_turns_collapse": avg(collapses, "turns_completed"),
        "average_patients_rescued_collapse": avg(collapses, "patients_rescued"),
        "average_patients_killed_collapse": avg(collapses, "patients_killed"),
        "average_house_damage_collapse": avg(collapses, "house_damage"),

        "average_turns_patient_loss": avg(patient_losses, "turns_completed"),
        "average_patients_rescued_patient_loss": avg(patient_losses, "patients_rescued"),
        "average_patients_killed_patient_loss": avg(patient_losses, "patients_killed"),
        "average_house_damage_patient_loss": avg(patient_losses, "house_damage"),
    }


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", default="intelligent")
    parser.add_argument("--num-agents", type=int, default=6)
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
