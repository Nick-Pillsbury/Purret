FROM python:3.14.3-slim

# Update and install v4l2 tools and ffmpeg
RUN apt-get update && apt-get install v4l-utils ffmpeg -y

WORKDIR /app
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir fastapi uvicorn

# Create recordings dir inside container, with will link to another location
RUN mkdir -p /recordings

# Expose API port
EXPOSE 8001

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]