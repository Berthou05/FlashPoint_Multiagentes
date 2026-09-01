import http.client
import json
import threading
import unittest

from http.server import HTTPServer

import server


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.model = None
        cls.httpd = HTTPServer(("127.0.0.1", 0), server.Server)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.thread.join()
        cls.httpd.server_close()

    def setUp(self):
        server.model = None

    def request_json(self, method, path, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        headers = {}
        payload = None

        if body is not None:
            payload = json.dumps(body)
            headers["Content-Type"] = "application/json"

        connection.request(method, path, body=payload, headers=headers)
        response = connection.getresponse()
        data = json.loads(response.read().decode("utf-8"))
        connection.close()
        return response.status, data

    def test_reset_initializes_four_skip_doctors_by_default(self):
        status, response = self.request_json("POST", "/reset", {})

        self.assertEqual(status, 200)
        self.assertEqual(len(response["game_state"]["doctors"]), 4)
        self.assertEqual(response["game_state"]["turn"], 0)

    def test_state_is_available_before_reset(self):
        status, response = self.request_json("GET", "/state")

        self.assertEqual(status, 200)
        self.assertEqual(len(response["game_state"]["doctors"]), 4)

    def test_step_starts_default_simulation_when_not_reset(self):
        status, response = self.request_json("POST", "/step", {})

        self.assertEqual(status, 200)
        self.assertEqual(response["game_state"]["turn"], 1)


if __name__ == "__main__":
    unittest.main()
