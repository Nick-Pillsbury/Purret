import os
import signal
import subprocess
from datetime import datetime
from fastapi import FastAPI

'''
v4l2-ctl --list-formats-ext - check camera outputs and frame rate


ffmpeg
-f v4l2                        - Video4Linux2, usb webs ect
-input_format mjpeg            - input foramt of frames from camera
-framerate 30                  - framerate to push / pull from camera
-video_size 1280x720           - resolution
-i /dev/video0                 - camera input
-c:v copy                      - copy exact frame from camer no recoding
-c:v libx264                   - encode to H.264
-preset ultrafast              - stream speed
-tune zerolatency              - stream speed
-f flv                         - format output for flash video conatiner standard for rtmp
rtmp://localhost:1935/mystream - push a rtmp stream to port 1935 preset rtmp in for media server

// mjpeg example with encoding
ffmpeg -f v4l2 -input_format mjpeg -framerate 30 -video_size 1280x720 -i /dev/video0 \
       -c:v libx264 -preset ultrafast -tune zerolatency -f flv rtmp://localhost:1935/stream

// h264 camera output example no encoding
ffmpeg -f v4l2 -input_format h264 -framerate 30 -video_size 1920x1080 -i /dev/video0 \
       -c copy -tune zerolatency -preset ultrafast -f flv rtmp://localhost:1935/stream

'''
import os
import signal
import subprocess
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()

# Track running processes
ffmpeg_process = None
recording_process = None

# Container path
recordings_dir = "/recordings"


# ---------- STREAM ----------
@app.post("/stream/start")
def start_stream():
    global ffmpeg_process

    if ffmpeg_process is not None:
        return {"status": "stream already running"}

    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "v4l2",
        "-input_format", "h264",
        "-framerate", "30",
        "-video_size", "1920x1080",
        "-i", "/dev/video0",
        "-c", "copy",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-f", "flv",
        "rtmp://localhost:1935/stream"
    ]

    ffmpeg_process = subprocess.Popen(ffmpeg_cmd)
    return {"status": "stream started", "pid": ffmpeg_process.pid}


@app.post("/stream/stop")
def stop_stream():
    global ffmpeg_process

    if ffmpeg_process is None:
        return {"status": "stream not running"}
    
    if recording_process is not None:
        return {"status": "stop recording before stopping stream"}

    ffmpeg_process.send_signal(signal.SIGINT)
    ffmpeg_process.wait()
    ffmpeg_process = None

    return {"status": "stream stopped"}


# ---------- RECORDING ----------
@app.post("/recording/start")
def start_recording():
    global recording_process

    if recording_process is not None:
        return {"status": "recording already running"}

    os.makedirs(recordings_dir, exist_ok=True)

    filename = os.path.join(
        recordings_dir,
        f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    )

    record_cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", "rtsp://localhost:8554/stream",
        "-c", "copy",
        filename
    ]

    recording_process = subprocess.Popen(record_cmd)

    return {"status": "recording started", "file": filename}


@app.post("/recording/stop")
def stop_recording():
    global recording_process

    if recording_process is None:
        return {"status": "recording not running"}

    recording_process.send_signal(signal.SIGINT)
    recording_process.wait()
    recording_process = None

    return {"status": "recording stopped"}


# ---------- STATUS ----------
@app.get("/status")
def status():
    return {
        "stream": "running" if ffmpeg_process else "stopped",
        "recording": "running" if recording_process else "stopped"
    }
