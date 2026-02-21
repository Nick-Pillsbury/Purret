# Video Streaming Container
This document outlines the tools, design decisions, configuration, and architecture of the Video Streaming Container.

---

## Hardware Requirements
This container is designed to run on:
- Raspberry Pi 5 (8GB)
- USB Webcam (`/dev/video0`)
- USB 3.0 External Storage (optional, for recording)

---

## Functionality
This container is responsible for:
- Receiving control commands via a C++ API
- Capturing video from a USB webcam
- Encoding video using H.264
- Streaming video via RTSP
- Optionally recording video to external storage

---

## Tools and Technology Stack

### 1. C++
C++ was selected due to its performance characteristics and low-latency capabilities. The system must operate in a resource-constrained environment, as multiple containers run concurrently on the Raspberry Pi 5.
**Benefits:**
- High performance  
- Low memory overhead  
- Fine-grained hardware control  
- Suitable for real-time processing  

---

### 2. FFmpeg
FFmpeg was selected for video processing and streaming because it provides:
- Reliable H.264 encoding support  
- Low-latency streaming capabilities  
- Hardware acceleration support on Raspberry Pi  
- Stable and production-proven multimedia handling  
Implementing video encoding from scratch would significantly increase complexity and development time.

---

### 3. RTSP (Real-Time Streaming Protocol)
RTSP was chosen as the streaming protocol because:
- Supported by Unity (via plugins or native solutions)  
- Designed for low-latency streaming  
- More efficient than HTTP-based streaming for real-time use  
- Works seamlessly with H.264 compression  
**Default streaming port:** `8554`

---

### 4. H.264 Compression
H.264 was selected due to:
- Hardware acceleration support on Raspberry Pi 5  
- High compression efficiency  
- Low bandwidth usage  
- Broad compatibility (including Unity clients)  

---

### 5. Docker
Docker was selected for containerization because it provides:
- Hardware device access support (`/dev/video0`, USB storage)  
- Service isolation between system components  
- Environment consistency across development and deployment  
- Simplified dependency management  
- Scalable and modular architecture  

---

## Container Architecture
```plaintext
    USB Webcam (/dev/video0)
            ↓
      FFmpeg Process
            ↓
   H.264 Hardware Encoding
            ↓
      RTSP Stream (8554)
         ↓            ↓
  WireGuard Tunnel   Local Unity Client
         ↓
     Remote Unity Client
```

---

## Video Storage
Recording is:
- Optional
- Not continuous
An external USB 3.0 thumb drive was used because:
- Short recording sessions
- Low sustained write duration
- Not 24/7 usage
- Super Cheap

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
   > Persistant Storage
   > ```
   >docker volume ls
   >docker volume create mydata
   >docker volume rm mydata
   >```
   >
   > Compose
   > ```
   >docker compose up -d
   >docker compose down
   >docker compose restart
   >docker compose logs -f
   >```