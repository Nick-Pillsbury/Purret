# Purret Project Proposal

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
- Motion smoothing and calibration routines
- Preset reset positions
- Safety mechanisms (angle limits, emergency stop, request limiting)
- Multiple speed and laser presets
- Container health checks and error reporting

---

## Master API
The Master API is the central coordinator of the system. It manages user commands, enforces system rules, and coordinates the hardware and video containers.

**Key Features**
- Endpoints for servo control, laser control, video recording, and telemetry
- System event logging and telemetry collection
- Single-user control enforcement with session tokens
- System-wide monitoring
- State machine implementation

---

## Frontend
The frontend provides the user-facing interface. It includes a Unity-based control interface for a single user and a spectator view for additional users.

**Key Features**
- Interface for controlling the laser turret
- User and spectator modes
- Real-time display of system status and telemetry
- Optional gamification elements (controller support, speed modes, laser modes)

---

## Milestones

### System Setup & Planning (January – Early February)
- Raspberry Pi and WireGuard setup
- Git repository initialization
- Research tools and libraries (Unity, OpenCV, FastAPI, C++)
- Initial architecture documentation and wireframes

### Basic and Mock Setup (End of February)
- Basic hardware wiring completed
- Servo movement testing
- Camera capture with static frame or test stream
- Skeleton API endpoints implemented
- Unity frontend connected to mock API

### Core Functionality Complete (End of March)
- Hardware fully controllable (servos and laser)
- Live video streaming operational
- Master API state machine functional
- Frontend displays real-time system status

### Primary Goals Completed & Polishing (End of April)
**Hardware**
- Servos calibrated and laser mounted
- Motion smoothing and safety limits implemented
- Emergency stop and reset presets functional

**Video**
- Live streaming stable
- Video recording implemented
- Stream health monitoring active

**Master API**
- All endpoints completed
- Single-user control enforced
- Telemetry and error logging implemented

**Frontend**
- Full control functionality implemented
- Gamification features added
- User and spectator modes complete

### Final Integration, Testing & Demo (Early May)
- Full system integration
- End-to-end testing
- Final documentation cleanup
- Working demo prepared

---

## Tech Stack
- Raspberry Pi
- C++ for hardware control and video capture
- Python (FastAPI) for the Master API
- Unity (C#) for the frontend
- Docker for containerization
- WireGuard for optional secure access

---

## Team Members
- **Nick Pillsbury** (Lead) – 4 credits – pillsn@rpi.edu  
- **Mark Evans** – 4 credits – evansm2@rpi.edu  
- **Tarik Baghdadi** – 4 credits – baghdt@rpi.edu  
- **Keith Wilfert** – 4 credits – wilfek@rpi.edu  
