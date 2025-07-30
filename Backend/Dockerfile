# === Stage 1: Builder ===
# Use a slim Python image for building dependencies
FROM python:3.10-slim-buster AS builder

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for some Python packages (e.g., opencv, ffmpeg)
# libgl1-mesa-glx is critical for headless OpenCV, build-essential for compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libgl1-mesa-glx \
    libjpeg-dev \
    zlib1g-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy your updated requirements.txt (without torch/torchvision)
COPY requirements.txt .

# Install Python dependencies, specifically targeting CPU-only PyTorch
# torch and torchvision are NOT in requirements.txt; installed here with --index-url
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu && \
    pip cache purge

# === Stage 2: Final Image ===
# Use a very minimal Python runtime image
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /app

# Copy only the necessary installed Python packages from the builder stage
# This copies the entire virtual environment's site-packages
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy your application code
COPY . .

# Create the directory for processed videos (if it doesn't exist already via git clone)
RUN mkdir -p processed_videos

# Expose the port your Flask app runs on
EXPOSE 5000

# Set environment variables for your application (e.g., for Flask and video saving)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PROCESSED_VIDEO_DIR=processed_videos # Matches your Python code's default

# Command to run your Gunicorn server
# Make sure 'app:app' matches your Flask app object (e.g., if it's in app.py and named `app`)
CMD ["gunicorn", "-w", "2", "--timeout", "120", "-b", "0.0.0.0:5000", "app:app"]
