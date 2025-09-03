FROM python:3.11-slim

# Install ffmpeg + clamav
RUN apt-get update && apt-get install -y ffmpeg clamav && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]