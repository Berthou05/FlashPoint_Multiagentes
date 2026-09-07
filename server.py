import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from plague_sim.entities import Door, POI, Patient, RatKing, RatSwarm, Wall
from plague_sim.model import PlagueSimulationModel


API_VERSION = "v1"
model = None
state_version = 0


def create_model(strategy="skip", num_agents=1, seed=None):
    global model, state_version
    model = PlagueSimulationModel(strategy=strategy, num_agents=num_agents, seed=seed)
    state_version = 0


def get_model():
    global model
    if model is None:
        create_model()
    return model


def build_state(simulation_model):
    """Build the Unity snapshot from the Mesa model."""
    walls = []
    doors = []

    for cells, boundary in simulation_model.boundaries.items():
        cell_a, cell_b = cells
        boundary_state = {
            "id": simulation_model.boundary_ids[cells],
            "ax": cell_a[0],
            "ay": cell_a[1],
            "bx": cell_b[0],
            "by": cell_b[1],
            "destroyed": boundary.is_destroyed,
        }
        if isinstance(boundary, Wall):
            boundary_state["damage"] = boundary.damage
            walls.append(boundary_state)
        else:
            boundary_state["open"] = boundary.is_open
            doors.append(boundary_state)

    active_doctor = simulation_model.doctors[simulation_model.active_doctor_index]
    state = {
        "width": simulation_model.width,
        "height": simulation_model.height,
        "turn": simulation_model.turn,
        "strategy": simulation_model.strategy,
        "phase": simulation_model.phase,
        "active_doctor_id": active_doctor.unique_id,
        "game_status": (
            "victory" if simulation_model.game_over and simulation_model.game_won
            else "defeat" if simulation_model.game_over
            else "running"
        ),
        "house_damage": simulation_model.house_damage,
        "patients_rescued": simulation_model.patients_rescued,
        "patients_killed": simulation_model.patients_killed,
        "walls": walls,
        "doors": doors,
        "rat_swarms": [],
        "rat_kings": [],
        "pois": [],
        "patients": [],
        "doctors": [],
    }

    entity_lists = {RatSwarm: "rat_swarms", RatKing: "rat_kings", POI: "pois", Patient: "patients"}
    for entity in simulation_model.agents:
        key = entity_lists.get(type(entity))
        if key is not None and entity.pos is not None:
            state[key].append({"id": entity.unique_id, "x": entity.pos[0], "y": entity.pos[1]})

    for doctor in simulation_model.doctors:
        carried_patient = doctor.carried_patient
        state["doctors"].append({
            "id": doctor.unique_id,
            "x": doctor.pos[0],
            "y": doctor.pos[1],
            "action_points": doctor.action_points,
            "carried_patient_id": carried_patient.unique_id if carried_patient is not None else -1,
        })

    return state


class Server(BaseHTTPRequestHandler):

    def _set_response(self, content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_game_response(self, events=None):
        self._set_response()
        response_data = {
            "api_version": API_VERSION,
            "state_version": state_version,
            "events": events or [],
            "state": build_state(get_model()),
        }
        self.wfile.write(json.dumps(response_data).encode("utf-8"))

    def do_OPTIONS(self):
        self._set_response()

    def do_GET(self):
        if self.path == "/":
            self._set_response()
            self.wfile.write(json.dumps({"api_version": API_VERSION, "status": "PlaguePoint server running"}).encode("utf-8"))
        elif self.path == "/state":
            self._send_game_response()
        else:
            self.send_error(404)

    def do_POST(self):
        global state_version

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if not isinstance(data, dict):
            self.send_error(400, "JSON body must be an object")
            return

        if self.path == "/reset":
            create_model(data.get("strategy", "skip"), data.get("num_agents", 1), data.get("seed"))
            self._send_game_response()
            return

        current_model = get_model()
        try:
            if self.path == "/step_doctor":
                events = current_model.step_doctor()
                state_version_increment = int(bool(events))
            elif self.path == "/step_environment":
                events = current_model.step_environment()
                state_version_increment = int(bool(events))
            elif self.path in ("/step_complete_turn", "/step"):
                events = current_model.step_complete_turn()
                state_version_increment = sum(event["type"] in ("doctor_turn_started", "environment_started") for event in events)
            else:
                self.send_error(404)
                return
        except (ValueError, RuntimeError) as error:
            self.send_error(409, str(error))
            return

        state_version += state_version_increment
        self._send_game_response(events)


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    httpd = server_class(("", port), handler_class)
    logging.info("Starting PlaguePoint server on port %s...", port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    logging.info("Stopping PlaguePoint server...")


if __name__ == "__main__":
    run()
