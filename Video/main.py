from fastapi import FastAPI
import subprocess
import os
import signal


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


app = FastAPI()

# Track running processes
ffmpeg_process = None
recording_process = None
media_server_process = None

# ---------- MEDIA SERVER ----------

@app.post("/media_server/start")
def start_media_server():
    global media_server_process
    if media_server_process is not None:
        return {"status": "already running"}

    # run MediaMTX via Docker
    cmd = [
        "docker", "run", "-d",
        "--name", "mediamtx",
        "-p", "1935:1935",
        "-p", "8889:8889",
        "bluenviron/mediamtx:latest"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"status": "error", "error": result.stderr}
    media_server_process = result.stdout.strip()
    return {"status": "started", "container_id": media_server_process}

@app.post("/media_server/stop")
def stop_media_server():
    global media_server_process
    if media_server_process is None:
        return {"status": "not running"}
    subprocess.run(["docker", "stop", "mediamtx"])
    subprocess.run(["docker", "rm", "mediamtx"])
    media_server_process = None
    return {"status": "stopped"}

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
        "-c:v", "copy",
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
    ffmpeg_process.terminate()
    ffmpeg_process = None
    return {"status": "stream stopped"}

# ---------- RECORDING ----------

@app.post("/recording/start")
def start_recording():
    global recording_process
    if recording_process is not None:
        return {"status": "recording already running"}

    record_cmd = [
        "ffmpeg",
        "-f", "v4l2",
        "-input_format", "h264",
        "-framerate", "30",
        "-video_size", "1920x1080",
        "-i", "/dev/video0",
        "-c:v", "copy",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-f", "mp4",
        "recording.mp4"
    ]
    recording_process = subprocess.Popen(record_cmd)
    return {"status": "recording started", "pid": recording_process.pid}

@app.post("/recording/stop")
def stop_recording():
    global recording_process
    if recording_process is None:
        return {"status": "recording not running"}
    recording_process.terminate()
    recording_process = None
    return {"status": "recording stopped"}


