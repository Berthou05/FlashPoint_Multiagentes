"""Run a game and print the JSON response after each simulation phase."""

import argparse
import json
import sys

from plague_sim.model import PlagueSimulationModel
from server import API_VERSION, build_state


def build_response(simulation_model, events, state_version):
    """Build the same response envelope that the server sends to Unity."""
    return {
        "api_version": API_VERSION,
        "state_version": state_version,
        "events": events,
        "state": build_state(simulation_model),
    }


def print_response(simulation_model, events, state_version):
    """Print one complete JSON response without any extra terminal text."""
    response = build_response(simulation_model, events, state_version)
    print(json.dumps(response, indent=2, sort_keys=True))


def wait_for_confirmation():
    """Wait until the user confirms the current complete turn with Y."""
    while True:
        print("Escribe Y para validar este turno y continuar: ", end="", file=sys.stderr, flush=True)
        if sys.stdin.readline().strip().upper() == "Y":
            return


def run_game(strategy="random", num_agents=1, seed=None, max_turns=500):
    """Run one complete turn at a time after terminal confirmation."""
    model = PlagueSimulationModel(strategy=strategy, num_agents=num_agents, seed=seed)
    state_version = 0

    while not model.game_over and model.doctor_turns_started < max_turns:
        doctor_events = model.step_doctor()
        state_version += 1
        print_response(model, doctor_events, state_version)

        if model.game_over:
            break

        environment_events = model.step_environment()
        state_version += 1
        print_response(model, environment_events, state_version)

        wait_for_confirmation()


def parse_arguments():
    """Read the options needed for a reproducible run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", default="random")
    parser.add_argument("--num-agents", type=int, default=1)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--max-turns", type=int, default=500)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    run_game(
        strategy=arguments.strategy,
        num_agents=arguments.num_agents,
        seed=arguments.seed,
        max_turns=arguments.max_turns,
    )
