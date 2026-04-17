import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

from fastapi.testclient import TestClient

MASTER_API_DIR = Path(__file__).resolve().parents[1]
if str(MASTER_API_DIR) not in sys.path:
    sys.path.insert(0, str(MASTER_API_DIR))

import main  # noqa: E402


class MasterApiEndpointTests(unittest.TestCase):
    def setUp(self):
        main.active_token = None
        main.servo1angle = 90
        main.servo2angle = 90
        self.client = TestClient(main.app)

    def login_headers(self):
        response = self.client.post("/login", json={"username": "tester"})
        self.assertEqual(response.status_code, 200)
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_safe_stop_turns_off_recording_stream_and_laser(self):
        headers = self.login_headers()

        with patch.object(
            main,
            "_camera_service_request",
            side_effect=[
                {"status": "recording stopped"},
                {"status": "stream stopped"},
            ],
        ) as camera_request, patch.object(
            main,
            "_servo_service_request",
            return_value={"status": "laser turned off"},
        ) as servo_request:
            response = self.client.post("/front/system/safe-stop", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "ok": True,
                "recording": {"status": "recording stopped"},
                "stream": {"status": "stream stopped"},
                "laser": {"status": "laser turned off"},
            },
        )
        self.assertEqual(
            camera_request.call_args_list,
            [
                call("POST", "/recording/stop"),
                call("POST", "/stream/stop"),
            ],
        )
        servo_request.assert_called_once_with("POST", "/laser/off")

    def test_servo_reset_recenters_both_axes(self):
        headers = self.login_headers()
        main.servo1angle = 15
        main.servo2angle = 165

        with patch.object(
            main,
            "_servo_service_request",
            side_effect=[
                {"angle": 90.0},
                {"angle": 90.0},
            ],
        ) as servo_request:
            response = self.client.post("/front/servo/reset", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(main.servo1angle, 90.0)
        self.assertEqual(main.servo2angle, 90.0)
        self.assertEqual(
            response.json(),
            {"ok": True, "servo1": {"angle": 90.0}, "servo2": {"angle": 90.0}},
        )
        self.assertEqual(
            servo_request.call_args_list,
            [
                call("POST", "/servo1/move", {"angle": 90.0}),
                call("POST", "/servo2/move", {"angle": 90.0}),
            ],
        )


if __name__ == "__main__":
    unittest.main()
