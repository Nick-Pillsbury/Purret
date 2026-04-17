import os
import signal
import subprocess
from fastapi import FastAPI
from datetime import datetime


# Globals
app = FastAPI()
ffmpeg_process = None
recording_process = None
recordings_dir = "/recordings" # /recordings in docker will be linked to /mnt/usb on host for persistent storage
# recordings_dir = "/mnt/usb"  # local testing


# Stream Start
# Start a ffmeg process to:
    # capture video from /dev/video0
    # encode it with h264
    # stream it with rtsp to media server on localhost:8554
@app.post("/stream/start")
def start_stream():
    global ffmpeg_process

    if ffmpeg_process is not None:
        return {"status": "stream already running"}
    
    cmd = [
        "ffmpeg",
        "-f", "v4l2",
        "-input_format", "mjpeg",
        "-video_size", "1280x720",
        "-framerate", "30",
        "-i", "/dev/video0",
        "-an",

        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",

        "-pix_fmt", "yuv420p",
        "-profile:v", "baseline",

        "-g", "30",

        "-f", "rtsp",
        "-rtsp_transport", "tcp",
        "rtsp://127.0.0.1:8554/stream"
    ]
    
    try:
        ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"status": "stream started"}
    except Exception as e:
        ffmpeg_process = None
        return {"status": "error", "error-message": str(e)}


# Stream Stop
# End the ffmpeg process that is streaming to rtsp server. 
# If recording is active, do not stop stream until recording is stopped first. 
    # Ending stream while recording will error out the recording process and corrupt the recording file.
@app.post("/stream/stop")
def stop_stream():
    global ffmpeg_process

    if ffmpeg_process is None:
        return {"status": "stream not running"}
    if recording_process is not None:
        return {"status": "stop recording before stopping stream"}
    
    try:
        ffmpeg_process.terminate()
        ffmpeg_process.wait(timeout=5)
    except Exception:
        ffmpeg_process.kill()
    finally:
        ffmpeg_process = None
    
    return {"status": "stream stopped"}


# Recording Start
# Start a ffmpeg process to:
    # Capture video from rtsp stream on localhost:8554
    # Save it to a file in /recordings with unique filename
@app.post("/recording/start")
def start_recording():
    global recording_process

    if recording_process is not None:
        return {"status": "recording already running"}

    if ffmpeg_process is None:
        return {"status": "stream not running"}

    os.makedirs(recordings_dir, exist_ok=True)
    filename = os.path.join(
        recordings_dir,
        f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    )

    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", "rtsp://127.0.0.1:8554/stream",
        "-c:v", "copy",
        filename
    ]

    try:
        recording_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"status": "recording started", "file": filename}
    except Exception as e:
        recording_process = None
        return {"status": "error", "message": str(e)}


# Recording Stop
# End the ffmpeg process that is recording the rtsp stream.
@app.post("/recording/stop")
def stop_recording():
    global recording_process

    if recording_process is None:
        return {"status": "recording not running"}

    try:
        recording_process.send_signal(signal.SIGINT)
        recording_process.wait(timeout=5)
    except Exception:
        recording_process.kill()
    finally:
        recording_process = None

    return {"status": "recording stopped"}


# Status
    # Return status of stream and recording processes.
@app.get("/status")
def status():
    return {
        "stream": "running" if ffmpeg_process else "stopped",
        "recording": "running" if recording_process else "stopped"
    }