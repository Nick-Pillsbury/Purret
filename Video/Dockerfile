FROM python:3.14.3-slim

# Install ffmpeg + v4l2 tools
RUN apt-get update && apt-get install -y
RUN apt-get install -y ffmpeg v4l-utils

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir fastapi uvicorn

# Create recordings dir inside container
RUN mkdir -p /recordings

# Expose API port
EXPOSE 8001

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]