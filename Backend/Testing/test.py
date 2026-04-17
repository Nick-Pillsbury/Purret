import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main  # noqa: E402


class PurretApiTests(unittest.TestCase):
    def setUp(self):
        main.active_token = None
        main.servo1angle = 90
        main.servo2angle = 90
        self.client = TestClient(main.app)

    def login(self):
        response = self.client.post("/login", json={"username": "tester"})
        self.assertEqual(response.status_code, 200)
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_system_status_reflects_login_state(self):
        self.assertEqual(self.client.get("/system-status").json(), {"session_active": False})

        headers = self.login()

        self.assertEqual(self.client.get("/system-status").json(), {"session_active": True})

        logout_response = self.client.post("/logout", headers=headers)
        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(self.client.get("/system-status").json(), {"session_active": False})

    def test_protected_route_requires_active_bearer_token(self):
        response = self.client.post("/front/laser/on")
        self.assertEqual(response.status_code, 401)

        self.login()
        invalid_token_response = self.client.post(
            "/front/laser/on",
            headers={"Authorization": "Bearer not-the-active-token"},
        )
        self.assertEqual(invalid_token_response.status_code, 403)

        headers = {"Authorization": f"Bearer {main.active_token}"}

        with patch.object(main, "_servo_service_request", return_value={"status": "ok"}) as servo_request:
            authed_response = self.client.post("/front/laser/on", headers=headers)

        self.assertEqual(authed_response.status_code, 200)
        self.assertEqual(authed_response.json(), {"ok": True, "status": "ok"})
        servo_request.assert_called_once_with("POST", "/laser/on")

    def test_servo_move_clamps_angles_before_proxying(self):
        headers = self.login()
        main.servo1angle = 179
        main.servo2angle = 1

        with patch.object(main, "_servo_service_request", side_effect=[
            {"angle": 180.0},
            {"angle": 0.0},
        ]) as servo_request:
            response = self.client.post(
                "/front/servo/move",
                headers=headers,
                json={"x": 1.0, "y": 1.0, "step": 30},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(main.servo1angle, 180.0)
        self.assertEqual(main.servo2angle, 0.0)
        self.assertEqual(
            response.json(),
            {"ok": True, "servo1": {"angle": 180.0}, "servo2": {"angle": 0.0}},
        )
        self.assertEqual(
            servo_request.call_args_list,
            [
                unittest.mock.call("POST", "/servo1/move", {"angle": 180.0}),
                unittest.mock.call("POST", "/servo2/move", {"angle": 0.0}),
            ],
        )

    def test_servo_reset_recenters_both_axes(self):
        headers = self.login()
        main.servo1angle = 15
        main.servo2angle = 165

        with patch.object(main, "_servo_service_request", side_effect=[
            {"angle": 90.0},
            {"angle": 90.0},
        ]) as servo_request:
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
                unittest.mock.call("POST", "/servo1/move", {"angle": 90.0}),
                unittest.mock.call("POST", "/servo2/move", {"angle": 90.0}),
            ],
        )

    def test_camera_health_proxies_status_payload(self):
        headers = self.login()

        with patch.object(
            main,
            "_camera_service_request",
            return_value={"stream": "running", "recording": "stopped"},
        ) as camera_request:
            response = self.client.get("/front/camera/health", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"ok": True, "stream": "running", "recording": "stopped"},
        )
        camera_request.assert_called_once_with("GET", "/status")


if __name__ == "__main__":
    unittest.main()
