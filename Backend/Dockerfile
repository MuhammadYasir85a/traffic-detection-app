# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies one by one to avoid cache invalidation
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies (CPU only, avoid torch + torchvision unless required)
RUN pip install flask gunicorn opencv-python-headless deep_sort_realtime numpy ultralytics

# Copy rest of the code
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Start the app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
