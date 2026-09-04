import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from plague_sim.model import PlagueSimulationModel


API_VERSION = "v1"
model = None
state_version = 0


def create_model(strategy="skip", num_agents=1, seed=None):
    global model, state_version

    model = PlagueSimulationModel(
        strategy=strategy,
        num_agents=num_agents,
        seed=seed,
    )
    state_version = 0


def get_model():
    """Return the current model, creating the default state if needed."""
    if model is None:
        create_model()

    return model


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
            "state": get_model().get_state(),
        }
        self.wfile.write(json.dumps(response_data).encode("utf-8"))

    def do_OPTIONS(self):
        self._set_response()

    def do_GET(self):
        if self.path == "/":
            self._set_response()
            self.wfile.write(json.dumps({
                "api_version": API_VERSION,
                "status": "PlaguePoint server running",
            }).encode("utf-8"))
            return

        if self.path == "/state":
            self._send_game_response()
            return

        self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if self.path == "/reset":
            strategy = data.get("strategy", "skip")
            num_agents = data.get("num_agents", 1)
            seed = data.get("seed")
            create_model(strategy, num_agents, seed)
            self._send_game_response()
            return

        current_model = get_model()

        try:
            if self.path == "/step_doctor":
                events = current_model.step_doctor()
                self._advance_state_version()
                self._send_game_response(events)
                return

            if self.path == "/step_environment":
                events = current_model.step_environment()
                self._advance_state_version()
                self._send_game_response(events)
                return

            if self.path in ("/step_complete_turn", "/step"):
                starting_phase = current_model.phase
                events = current_model.step_complete_turn()
                self._advance_state_version(2 if starting_phase == "doctor" else 1)
                self._send_game_response(events)
                return
        except (ValueError, RuntimeError) as error:
            self.send_error(409, str(error))
            return

        self.send_error(404)

    @staticmethod
    def _advance_state_version(amount=1):
        global state_version
        state_version += amount


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    logging.info("Starting PlaguePoint server on port %s...", port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    logging.info("Stopping PlaguePoint server...")


if __name__ == "__main__":
    run()
