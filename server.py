import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from plague_sim.model import PlagueSimulationModel


model = None


def create_model(seed=None):
    global model
    model = PlagueSimulationModel(seed=seed)


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
            if model:
                self._set_response()
                self.wfile.write(json.dumps({
                    "game_state": model.get_state()
                }).encode('utf-8'))
            else:
                self.send_error(400, "Model not initialized")

        else:
            self.send_error(404)

    def do_POST(self):
        global model

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data) if post_data else {}

        if self.path == '/step':
            if model:
                model.step()

                self._set_response()
                self.wfile.write(json.dumps({
                    "status": "Turn completed",
                    "game_state": model.get_state()
                }).encode('utf-8'))
            else:
                self.send_error(400, "Model not initialized")

        elif self.path == '/reset':
            seed = data.get('seed')

            create_model(seed)

            self._set_response()
            self.wfile.write(json.dumps({
                "status": "Game initialized",
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