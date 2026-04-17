# Purret Control API

This backend exposes the FastAPI service defined in `main.py`. It acts as the master control API for Purret and forwards requests to separate camera and servo services.

## What It Does

- Creates a single active control session with bearer-token auth
- Proxies camera commands to the camera service
- Proxies servo and laser commands to the servo service
- Exposes both `/front/...` routes for frontend use and direct service routes like `/camera/...` and `/servo1/...`

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic

## Project Files

- `main.py`: main FastAPI app
- `requirements.txt`: Python dependencies
- `Dockerfile`: container image for the API
- `endpoints.md`: earlier endpoint planning notes
- `WIREGUARD.md`: notes for running the API over WireGuard

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API from the `Backend` directory:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open the interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Run With Docker

Build and run from the `Backend` directory:

```bash
docker build -t purret-api .
docker run --rm -p 8000:8000 purret-api
```

## Environment Variables

The API forwards requests to two other services. These environment variables control where those services live:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PURR_CAMERA_SERVICE_URL` | `http://127.0.0.1:8001` | Base URL for the camera service |
| `PURR_CAMERA_SERVICE_TIMEOUT_S` | `5` | Timeout for camera requests |
| `PURR_SERVO_SERVICE_URL` | `http://127.0.0.1:8002` | Base URL for the servo service |
| `PURR_SERVO_SERVICE_TIMEOUT_S` | `5` | Timeout for servo requests |

## Authentication Model

The API allows only one active session at a time.

1. `POST /login` returns a bearer token.
2. Send that token in the `Authorization` header for protected routes.
3. `POST /logout` clears the active session.

Example:

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"operator\"}"
```

Response:

```json
{
  "token": "your-session-token"
}
```

Use the token:

```bash
curl -X GET http://127.0.0.1:8000/system-status

curl -X POST http://127.0.0.1:8000/front/camera/start \
  -H "Authorization: Bearer your-session-token"
```

## Request Models

### `LoginRequest`

```json
{
  "username": "operator"
}
```

### `ServoMoveRequest`

You can control the combined servo movement in three ways:

By direction:

```json
{
  "direction": "up_right",
  "step": 5
}
```

By vector:

```json
{
  "vector": [1.0, 0.5],
  "step": 10
}
```

By x/y values:

```json
{
  "x": -0.5,
  "y": 1.0,
  "step": 5
}
```

Valid `direction` values:

- `up`
- `down`
- `left`
- `right`
- `up_left`
- `up_right`
- `down_left`
- `down_right`
- `stop`

### `ServoAxisMoveRequest`

```json
{
  "angle": 90
}
```

## Endpoints

### Public

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/login` | Starts a session and returns a bearer token |
| `POST` | `/logout` | Clears the active session |
| `GET` | `/system-status` | Returns whether a session is active |

### Frontend Control Routes

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/front/servo/move` | Moves the turret using joystick-like input |
| `POST` | `/front/servo/reset` | Resets both servos back to 90 degrees |
| `POST` | `/front/system/safe-stop` | Stops recording, stops the stream, and turns the laser off |
| `POST` | `/front/camera/start` | Starts camera streaming |
| `POST` | `/front/camera/stop` | Stops camera streaming |
| `POST` | `/front/camera/record/start` | Starts recording |
| `POST` | `/front/camera/record/stop` | Stops recording |
| `GET` | `/front/camera/health` | Gets camera status |
| `POST` | `/front/laser/on` | Turns laser on |
| `POST` | `/front/laser/off` | Turns laser off |
| `POST` | `/front/servo1/move` | Moves servo 1 to an absolute angle |
| `POST` | `/front/servo2/move` | Moves servo 2 to an absolute angle |

### Direct Camera Routes

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/camera/start` | Starts camera streaming |
| `POST` | `/camera/stop` | Stops camera streaming |
| `POST` | `/camera/record/start` | Starts recording |
| `POST` | `/camera/record/stop` | Stops recording |
| `GET` | `/camera/health` | Gets camera status |

### Direct Servo Routes

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/servo/move` | Moves both servos using joystick-like input |
| `POST` | `/servo/reset` | Resets both servos back to 90 degrees |
| `POST` | `/servo1/move` | Moves servo 1 to an absolute angle |
| `POST` | `/servo2/move` | Moves servo 2 to an absolute angle |
| `GET` | `/servo/health` | Gets servo service status |

### Direct System Routes

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/system/safe-stop` | Stops recording, stops the stream, and turns the laser off |

## Example Requests

Move the turret:

```bash
curl -X POST http://127.0.0.1:8000/front/servo/move \
  -H "Authorization: Bearer your-session-token" \
  -H "Content-Type: application/json" \
  -d "{\"direction\":\"left\",\"step\":5}"
```

Turn the laser on:

```bash
curl -X POST http://127.0.0.1:8000/front/laser/on \
  -H "Authorization: Bearer your-session-token"
```

Check camera health:

```bash
curl -X GET http://127.0.0.1:8000/front/camera/health \
  -H "Authorization: Bearer your-session-token"
```

Move servo 1 directly:

```bash
curl -X POST http://127.0.0.1:8000/servo1/move \
  -H "Authorization: Bearer your-session-token" \
  -H "Content-Type: application/json" \
  -d "{\"angle\":120}"
```

## Error Behavior

- Returns `403` if a protected route is called without the active token
- Returns `403` on login if another session is already active
- Returns `502` if the camera or servo service is unreachable or returns a bad response

## Notes

- `main.py` imports `chat.py` and includes `chat_router`, so that file needs to be present for the app to start successfully.
- Camera and servo actions depend on separate services being available at their configured URLs.
- FastAPI docs at `/docs` are the best source for the live schema if routes change.
