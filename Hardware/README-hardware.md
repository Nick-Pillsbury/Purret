# Purret — WiFi-Enabled Cat Laser Turret

A 2-DOF servo-driven pan-tilt laser turret controlled over WiFi, designed for interactive play with cats. The system combines a Raspberry Pi hardware backend, live video streaming, a centralized API, and a Unity-based frontend — all containerized with Docker.

> **Status:** In progress — core hardware assembled, laser module integration pending.

---

## Table of Contents

<!-- 1. [System Overview](#system-overview) -->
1. [Bill of Materials (BOM)](#bill-of-materials)
2. [Wiring & Pinout](#wiring--pinout)
3. [Assembly Instructions](#assembly-instructions)
4. [Firmware Installation](#firmware-installation)
5. [Usage & Safety](#usage--safety)
6. [TODO](#todo)

---

<!-- ## System Overview

Purret is composed of four modular components that communicate over a private Docker network:

| Component | Description |
|---|---|
| **Hardware Control Container** | C++ — controls pan/tilt servos and laser; enforces safety limits and motion smoothing |
| **Video Capture & Streaming Container** | C++ — captures and streams the live camera feed over WiFi; supports recording |
| **Master API** | Python / FastAPI — central orchestrator; enforces single-user control, session tokens, state machine, and telemetry |
| **Frontend** | Unity (C#) — game-style UI for laser control; spectator view, real-time status overlays, optional gamification |

**Tech Stack:** Raspberry Pi · C++ · Python/FastAPI · Unity (C#) · Docker · WireGuard (optional) -->

---

## Bill of Materials

| # | Component | Model / Notes | Link |
|---|-----------|---------------|------|
| 1 | 2-DOF Pan-Tilt Servo Kit | Yahboom — includes aluminum alloy bracket, 270° servo (top/pan), 180° servo (bottom/tilt) | [Amazon](https://www.amazon.com/Yahboom-Pan-Tilt-Electric-Platform-Accessories/dp/B0BRXVFCKX) |
| 2 | Servo Driver Module | HiLetgo PCA9685 — 16-channel, 12-bit PWM | [Amazon](https://www.amazon.com/HiLetgo-PCA9685-Channel-12-Bit-Arduino/dp/B07BRS249H) |
| 3 | Single-Board Computer | Raspberry Pi (exact model — **TODO**) | — |
| 4 | Laser Module | HiLetgo 650nm Diode Laser, 5V | [Amazon](https://www.amazon.com/HiLetgo-10pcs-650nm-Diode-Laser/dp/B071FT9HSV) |
| 5 | Camera Module | USB camera attached to chassis — model **TODO** | — |
| 6 | External Power Supply | Adjustable voltage — replaces original 7.4V battery plan | — |

### Servo Specifications

| | Top Servo (Pan) | Bottom Servo (Tilt) |
|---|---|---|
| Range | 0° – 270° | 0° – 180° |
| Torque | 20 kg·cm | 25 kg·cm |
| Required Voltage | 6 – 7.4 V | **TODO** |
| Position | Top of chassis | Bottom of chassis |

**PWM Pulse Reference (shared by both servos):**

| Pulse Width | Angle |
|-------------|-------|
| 0.5 ms | 0° |
| 1.0 ms | 45° |
| 1.5 ms | 90° |
| 2.0 ms | 135° |
| 2.5 ms | 180° |

---

## Wiring & Pinout

### PCA9685 Driver → Raspberry Pi

| Driver Pin | Raspberry Pi Physical Pin |
|------------|--------------------------|
| V+ | Pin 1 (3.3V) |
| GND | Pin 6 (GND) |
| SDA | Pin 3 (GPIO 2) |
| SCL | Pin 5 (GPIO 3) |

### Servo Motors → PCA9685 Driver

Connect each servo's three wires to the corresponding channel on the driver board, matching wire colors to the board labels. Channels used: **TODO** (confirm after physical wiring).

### Power Supply → PCA9685 Driver

The driver's V+ rail is powered externally by the adjustable power supply. Set supply voltage to 5V for optimal performance. [Do not exceed 6V](#usage--safety). The positive line connects to the V+ screw terminal (red side).

> **Note:** Do not power the servos from the Raspberry Pi's 5V rail — the servos require higher voltage and current than the Pi can safely provide.

### Camera → Raspberry Pi

The USB camera connects directly to a USB port on the Raspberry Pi.

### Laser Module → Raspberry Pi

> **See [TODO](#todo)** — laser module wiring is pending additional parts and is not yet connected.

Current plan: Laser needs to be connected to a switch drive + Current driver to be safely added to device.

### TODO - ADD LASER MODULE SUPPLIES

---

## Assembly Instructions

> Full step-by-step assembly instructions — **TODO** (will be updated as construction completes).

**Reference Materials:**
- Yahboom company GitHub: [YahboomTechnology/2DOF-PTZ](https://github.com/YahboomTechnology/2DOF-PTZ)
- Assembly video: [YouTube](https://www.youtube.com/watch?v=CBgL3jvkomg)
- Pi ↔ Control board wiring tutorial: [YouTube](https://www.youtube.com/watch?v=GwpSpOwvx9Y)

**Current build state:** Servo kit assembled and mounted to chassis. PCA9685 driver connected to Raspberry Pi. Camera attached to chassis. Power supply connected to driver.

---

## Firmware Installation

> **TODO** — C++ API for Raspberry Pi servo and laser control is under development.

**Planned approach:**
- Raspberry Pi communicates with PCA9685 via I2C
- Custom C++ API handles servo angle commands and laser actuation
- All containers run via Docker on the Pi
- Access/development via SSH over network (WireGuard optional for remote access)

---

## Usage & Safety

> **TODO** — will be filled in once the control system is complete.

**Preliminary safety notes:**
- **Never** point the laser at eyes or reflective surfaces
- Ensure power supply voltage is correctly set before powering servos — overvoltage will cause abnormal motor behavior; the 270° pan servo requires 6–7.4 V minimum
- The system enforces **maximum angle limits** and an **emergency stop** in the hardware container to prevent servo damage
- Only **one user at a time** can control the laser; additional users access a spectator-only view (enforced by Master API session tokens)
- Command request rate limiting is implemented to prevent servo burnout
- **Driver Board** has a max Voltage of 6V **DO NOT** supply with more or the board will break

---


## TODO

### Hardware
- [ ] **Laser module construction** — arrived but requires additional components; wiring plan (PIN 7) subject to change once parts confirmed
- [ ] Confirm PCA9685 channel assignments for each servo after final wiring
- [ ] Identify and document exact Raspberry Pi model
- [ ] Document exact camera model
- [ ] Confirm bottom servo (180°) voltage requirements
- [ ] Complete and document final wiring with photos
- [ ] Add wiring diagram image

### Software / Firmware
- [ ] Write and document C++ hardware control API (servo + laser)
- [ ] Implement motion smoothing and max angle safety limits
- [ ] Implement emergency stop and command rate limiting
- [ ] Implement preset reset position
- [ ] Set up Docker containers for all four components

### Documentation
- [ ] Assembly instructions (step-by-step with photos)
- [ ] Firmware installation guide
- [ ] Full Usage & Safety section
- [ ] API endpoint documentation
