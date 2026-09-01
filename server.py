import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from plague_sim.model import PlagueSimulationModel


model = None


def create_model(strategy="skip", num_agents=4, seed=None):
    global model

    model = PlagueSimulationModel(
        strategy=strategy,
        num_agents=num_agents,
        seed=seed
    )


def get_model():
    """Return the current model, creating the default state if needed."""
    if model is None:
        create_model()

    return model


class Server(BaseHTTPRequestHandler):

    def _set_response(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_response()

    def do_GET(self):
        global model

        if self.path == '/':
            self._set_response()
            self.wfile.write(json.dumps({
                "status": "PlaguePoint server running"
            }).encode('utf-8'))

        elif self.path == '/state':
            current_model = get_model()
            self._set_response()
            self.wfile.write(json.dumps({
                "game_state": current_model.get_state()
            }).encode('utf-8'))

        else:
            self.send_error(404)

    def do_POST(self):
        global model

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data) if post_data else {}

        if self.path == '/step':
            current_model = get_model()
            current_model.step()

            self._set_response()
            self.wfile.write(json.dumps({
                "status": "Turn completed",
                "game_state": current_model.get_state()
            }).encode('utf-8'))

        elif self.path == '/reset':
            strategy = data.get('strategy', 'skip')
            num_agents = data.get('num_agents', 4)
            seed = data.get('seed')

            create_model(
                strategy,
                num_agents,
                seed
            )

            self._set_response()
            self.wfile.write(json.dumps({
                "status": f"Game initialized with {num_agents} doctor(s)",
                "game_state": model.get_state()
            }).encode('utf-8'))

        else:
            self.send_error(404)


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    logging.info(f"Starting PlaguePoint server on port {port}...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    logging.info("Stopping PlaguePoint server...")


if __name__ == '__main__':
    run()
