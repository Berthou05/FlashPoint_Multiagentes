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

    def test_reset_initializes_one_skip_doctor_by_default(self):
        status, response = self.request_json("POST", "/reset", {})

        self.assertEqual(status, 200)
        self.assertEqual(set(response), {
            "api_version", "state_version", "events", "state",
        })
        self.assertEqual(response["api_version"], "v1")
        self.assertEqual(response["state_version"], 0)
        self.assertEqual(len(response["state"]["doctors"]), 1)
        self.assertEqual(response["state"]["turn"], 0)
        self.assertEqual(response["events"], [])
        self.assertNotIn("null", json.dumps(response))

    def test_state_is_available_before_reset(self):
        status, response = self.request_json("GET", "/state")

        self.assertEqual(status, 200)
        self.assertEqual(response["api_version"], "v1")
        self.assertEqual(len(response["state"]["doctors"]), 1)

    def test_step_starts_default_simulation_when_not_reset(self):
        status, response = self.request_json("POST", "/step", {})

        self.assertEqual(status, 200)
        self.assertEqual(response["state_version"], 2)
        self.assertEqual(response["state"]["turn"], 1)

    def test_step_doctor_returns_complete_doctor_turn_response(self):
        status, response = self.request_json("POST", "/step_doctor", {})

        self.assertEqual(status, 200)
        self.assertEqual(response["api_version"], "v1")
        self.assertEqual(response["state_version"], 1)
        self.assertEqual(response["state"]["phase"], "environment")
        self.assertEqual(response["events"][0]["type"], "doctor_turn_started")
        self.assertEqual(response["events"][-1]["type"], "doctor_turn_ended")

    def test_environment_and_complete_turn_endpoints_return_ordered_events(self):
        self.request_json("POST", "/reset", {})
        self.request_json("POST", "/step_doctor", {})

        status, response = self.request_json("POST", "/step_environment", {})

        self.assertEqual(status, 200)
        self.assertEqual(response["state_version"], 2)
        self.assertEqual(response["state"]["turn"], 1)
        self.assertEqual(
            [event["sequence"] for event in response["events"]],
            list(range(1, len(response["events"]) + 1)),
        )

        status, response = self.request_json("POST", "/step_complete_turn", {})

        self.assertEqual(status, 200)
        self.assertEqual(response["state_version"], 4)
        self.assertEqual(response["state"]["turn"], 2)
        self.assertIn(
            "environment_started",
            [event["type"] for event in response["events"]],
        )

    def test_state_does_not_advance_state_version(self):
        self.request_json("POST", "/reset", {})

        _, first_response = self.request_json("GET", "/state")
        _, second_response = self.request_json("GET", "/state")

        self.assertEqual(first_response["state_version"], 0)
        self.assertEqual(second_response["state_version"], 0)

    def test_step_from_environment_advances_state_version_once(self):
        self.request_json("POST", "/reset", {})
        self.request_json("POST", "/step_doctor", {})

        status, response = self.request_json("POST", "/step", {})

        self.assertEqual(status, 200)
        self.assertEqual(response["state_version"], 2)


if __name__ == "__main__":
    unittest.main()
