# Video Streaming Container
This document outlines the tools, design decisions, configuration, and architecture of the Video Streaming Container.

---

## Overview
This container runs a FastAPI-based video service that manages live streaming and recording using FFmpeg. It captures video from a local device, streams it over RTSP, and allows recordings of that stream to be saved to persistent storage. The API provides endpoints to start/stop streaming, start/stop recording, and check system status. It also ensures safe operation by preventing the stream from stopping while a recording is in progress.

---

## Functionality
This container is responsible for:
- Receiving control commands via a Python API
- Capturing video from a USB webcam
- Encoding video using H.264
- Streaming video via RTSP
- Recording video to external storage

---

## Tools and Technology Stack

### 1. Python FastAPI
FastAPI was selected due to its ease of use and high compatibility. It's best for:
- Compatibility across clients and platforms
- Ease of development and maintenance
- Well-maintained and fast framework

### 2. FFmpeg
FFmpeg was selected for video processing and streaming because it provides:
- H.264 encoding support  
- Low-latency streaming capabilities  
- Well know tool for capturing and streaming via mutiple different protocols

### 3. MediaMTX
MediaMTX was selected as the streaming server because of:
- Compatibility with RTSP/HLS/WebRTC clients
- Low resource usage
- Ability to ingest RTSP from the Pi and redistribute to multiple clients at once and over many protocols

### 4. RTSP (Real-Time Streaming Protocol)
RTSP was chosen as the streaming protocol because:
- Designed for low-latency streaming
- More efficient than HTTP-based streaming for real-time use
- Works better with H.264 compression
**Default streaming port:** `8554`

### 5. H.264 Compression
H.264 was selected due to:
- High compression efficiency
- Low bandwidth usage

---

### 6. Docker
Docker was selected for containerization because it provides:
- Hardware device access support (`/dev/video0`, USB storage)  
- Service isolation between system components
- Environment consistency across development and deployment
- Simplified dependency management
- Scalable and modular architecture

---

## Stream Architecture
```plaintext
    USB Webcam (/dev/video0)
            ↓
      FFmpeg Process
            ↓
      RTSP Stream (8554)
            ↓
        MediaMTX Server
         ↓            ↓
  WireGuard Tunnel   Local Unity Client
         ↓
Remote Unity Client
```

---

## Video Storage
An external USB 3.0 thumb drive was used because:
- Short recording sessions
- Super Cheap
- Better reading and writing lifespan (Preserve mirco sd card)

---

## Docker Commands
   > Container Controls
   >``` 
   >docker start <container>
   >docker stop <container>
   >docker restart <container>
   >docker rm <container>
   >docker logs <container>
   >docker exec -it <container> bash
   >```
   >
   > List containers
   > ```
   >docker ps
   >```
   >
   > Compose
   > ```
   >docker compose up -d
   >docker compose down
   >docker compose restart
   >docker compose logs -f
   >```