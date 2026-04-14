FROM python:3.14.3-slim

# Update and install v4l2 tools and ffmpeg
RUN apt-get update && apt-get install v4l-utils ffmpeg -y

WORKDIR /app
COPY main.py .
COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Create recordings dir inside container, with will link to another location
RUN mkdir -p /recordings

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]