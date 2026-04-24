# Servo Control API

This backend exposes the FastAPI service defined in `main.py`. It provides direct hardware control over two servos and a laser/LED module.

## What It Does

- Moves individual servos to absolute angle positions
- Sets and resets servo default positions
- Controls laser power (on, off, or PWM brightness)

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic

## Project Files

- `main.py`: main FastAPI app
- `servo_control.py`: low-level servo and LED control logic
- `requirements.txt`: Python dependencies

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open the interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Request Models

### `MoveRequest`

Used to move a single servo to an absolute angle:

```json
{
  "angle": 90.0
}
```

### `SetDefaultsRequest`

Used to set default angles for both servos:

```json
{
  "angle1": 90.0,
  "angle2": 45.0
}
```

### `BrightnessRequest`

Used to set laser brightness via PWM:

```json
{
  "value": 0.75
}
```

| Field   | Type  | Range     | Description                         |
| ------- | ----- | --------- | ----------------------------------- |
| `value` | float | 0.0 – 1.0 | Brightness level (0 = off, 1 = full) |

## Endpoints

### Servo Routes

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/servo1/move` | Moves servo 1 to an absolute angle |
| `POST` | `/servo2/move` | Moves servo 2 to an absolute angle |
| `POST` | `/servos/set_angles` | Sets the default angles for both servos |
| `POST` | `/servos/reset` | Resets both servos to their default positions |

### Laser Routes

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/laser/on` | Turns the laser on at full brightness |
| `POST` | `/laser/off` | Turns the laser off |
| `POST` | `/laser/pwm` | Sets laser brightness via PWM (0.0 – 1.0) |

## Example Requests

Move servo 1 to 90°:

```bash
curl -X POST http://127.0.0.1:8000/servo1/move \
  -H "Content-Type: application/json" \
  -d "{\"angle\": 90.0}"
```

Set default angles for both servos:

```bash
curl -X POST http://127.0.0.1:8000/servos/set_angles \
  -H "Content-Type: application/json" \
  -d "{\"angle1\": 90.0, \"angle2\": 45.0}"
```

Reset servos to defaults:

```bash
curl -X POST http://127.0.0.1:8000/servos/reset
```

Turn the laser on:

```bash
curl -X POST http://127.0.0.1:8000/laser/on
```

Set laser to 50% brightness:

```bash
curl -X POST http://127.0.0.1:8000/laser/pwm \
  -H "Content-Type: application/json" \
  -d "{\"value\": 0.5}"
```

## Error Behavior

- Returns `400` if an angle or brightness value is out of the accepted range
