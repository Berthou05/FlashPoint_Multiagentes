"""Run PlaguePoint simulations with Mesa batch_run and DataCollector."""

import argparse
import csv
import json
from collections import defaultdict

from mesa.batchrunner import batch_run

from plague_sim.model import PlagueSimulationModel


def average(values):
    return sum(values) / len(values) if values else None


def summarize_results(results):
    """Return the same main aggregate statistics used by the previous batch script."""
    wins = [result for result in results if result["result"] == "victory"]
    losses = [result for result in results if result["result"] != "victory"]
    collapses = [result for result in losses if result.get("end_reason") == "collapse"]
    patient_losses = [result for result in losses if result.get("end_reason") == "patients_killed_4"]
    truncated = [result for result in losses if result["result"] == "running"]

    def avg(group, key):
        return average([result[key] for result in group])

    games = len(results)
    failures = len(losses)
    seeds = sorted(result["seed"] for result in results)

    return {
        "strategy": results[0]["strategy"],
        "num_agents": results[0]["num_agents"],
        "games": games,
        "seed_start": seeds[0],
        "seed_end": seeds[-1],
        "successes": len(wins),
        "failures": failures,
        "win_rate": len(wins) / games if games else 0,
        "losses_by_collapse": len(collapses),
        "losses_by_patients": len(patient_losses),
        "truncated_at_limit": len(truncated),
        "collapse_rate_all_games": len(collapses) / games if games else 0,
        "patient_loss_rate_all_games": len(patient_losses) / games if games else 0,
        "truncated_rate_all_games": len(truncated) / games if games else 0,
        "collapse_share_of_failures": len(collapses) / failures if failures else 0,
        "patient_loss_share_of_failures": len(patient_losses) / failures if failures else 0,
        "truncated_share_of_failures": len(truncated) / failures if failures else 0,
        "average_turns_won": avg(wins, "turns_completed"),
        "average_turns_lost": avg(losses, "turns_completed"),
        "average_patients_rescued": avg(results, "patients_rescued"),
        "average_patients_killed": avg(results, "patients_killed"),
        "average_house_damage": avg(results, "house_damage"),
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


def run_plague_batch(strategies, num_agents_values, games=100, seed_start=1, max_turns=500, workers=None, progress=False):
    """Run every strategy/doctor-count combination with the same consecutive seeds."""
    parameters = {
        "strategy": strategies,
        "num_agents": num_agents_values,
    }
    seeds = list(range(seed_start, seed_start + games))

    results = batch_run(
        PlagueSimulationModel,
        parameters=parameters,
        rng=seeds,
        number_processes=workers,
        data_collection_period=-1,
        max_steps=max_turns,
        display_progress=progress,
    )

    results.sort(key=lambda result: (result["strategy"], result["num_agents"], result["seed"]))

    grouped = defaultdict(list)
    for result in results:
        grouped[(result["strategy"], result["num_agents"])].append(result)

    summaries = [summarize_results(group) for group in grouped.values()]
    summaries.sort(key=lambda summary: (summary["strategy"], summary["num_agents"]))
    return results, summaries


def save_raw_results(results, filename):
    """Save the final DataCollector row from every simulation to CSV."""
    if not results:
        return

    fieldnames = list(results[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", nargs="+", default=["intelligent"])
    parser.add_argument("--num-agents", nargs="+", type=int, default=[6])
    parser.add_argument("--max-turns", type=int, default=500)
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--workers", "--processes", dest="workers", type=int, default=None)
    parser.add_argument("--save-raw", default=None, help="Optional CSV filename for one final row per simulation.")
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    results, summaries = run_plague_batch(
        strategies=arguments.strategy,
        num_agents_values=arguments.num_agents,
        games=arguments.games,
        seed_start=arguments.seed_start,
        max_turns=arguments.max_turns,
        workers=arguments.workers,
        progress=arguments.progress,
    )

    if arguments.save_raw:
        save_raw_results(results, arguments.save_raw)

    output = summaries[0] if len(summaries) == 1 else summaries
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
