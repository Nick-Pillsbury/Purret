# Purret Project

## Overall Vision
Purret is a WiFi-enabled laser turret designed for interactive play with cats. The project combines hardware control, video streaming, and a gamified frontend to allow remote control of a laser pointer in a fun and engaging way.

The system is composed of four modular components that communicate over a private Docker network:
- Hardware Control Container
- Video Capture and Streaming Container
- Master API
- Frontend

This modular design allows independent development and testing while maintaining safe and synchronized operation.

---

## Video Capture and Streaming Container
This container handles camera input and streams live video over the local WiFi network so users can see the laser pointer in real time. It also supports video recording and health monitoring.

**Key Features**
- Capture live video
- Stream video over WiFi
- Record video to persistent storage
- Monitor stream and container health
- Error reporting
- API for communication with the Master API

---

## Hardware Control Container
This container manages all physical interactions with the turret, including pan/tilt servos and the laser pointer. It enforces safety limits and smooth motion to prevent hardware damage.

**Key Features**
- Servo control and laser actuation
- API for communication
- Preset reset positions
- Safety mechanisms (angle limits, emergency stop, request limiting)
- Speed controls
- Container health checks and error reporting

---

## Master API
The Master API is the central coordinator of the system. It manages user commands, enforces system rules, and coordinates the hardware and video containers.

**Key Features**
- Endpoints for servo control, laser control, video recording, and telemetry
- System event logging and telemetry collection
- Single-user control enforcement with session tokens
- System-wide monitoring

---

## Frontend
The frontend provides the user-facing interface. It includes a Unity-based control interface for a single user and a spectator view for additional users.

**Key Features**
- Interface for controlling the laser turret
- User and spectator modes
- Optional gamification elements

---

## Tech Stack

| Layer | Technology |
|---|---|
| Hardware & Video Control | Python (subprocess, serial) |
| API Services | Python, FastAPI |
| Media Server | MediaMTX |
| Video Processing | ffmpeg |
| Frontend | Unity (C#) |
| Containerization | Docker |
| Networking | WireGuard (remote access) |
| Hardware Platform | Raspberry Pi |

---

## Team Members
- **Nick Pillsbury** (Lead) – 4 credits – pillsn@rpi.edu  
- **Mark Evans** – 4 credits – evansm2@rpi.edu  
- **Tarik Baghdadi** – 4 credits – baghdt@rpi.edu  
- **Keith Wilfert** – 4 credits – wilfek@rpi.edu  
