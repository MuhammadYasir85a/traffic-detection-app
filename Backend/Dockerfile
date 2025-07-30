# === Stage 1: Builder ===
# Use a slim Python image for smaller base size
FROM python:3.10-slim-buster AS builder
# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for OpenCV, PyTorch, etc.
# --no-install-recommends reduces size by not installing suggested packages
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

# Install CPU-only PyTorch and Torchvision FIRST.
# This is CRUCIAL so that 'ultralytics' finds the CPU version already installed.
RUN pip install --no-cache-dir torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu

# Copy your requirements.txt into the builder stage
COPY requirements.txt .

# Install other Python dependencies from requirements.txt
# 'ultralytics' will now link to the CPU-only PyTorch installed above.
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge # Clean up pip cache to save space

# === Stage 2: Final Image ===
# Start from a clean, slim Python image again for the final build
FROM python:3.10-slim-buster
WORKDIR /app

# Copy only the installed Python packages from the builder stage
# This significantly reduces the final image size by excluding build tools and temporary files
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy your application code into the final image
# Since Render's Root Directory will be 'Backend/', '.' refers to the content of 'Backend/'
COPY . .

# Create the directory where processed videos might be stored (if applicable)
RUN mkdir -p processed_videos

# Expose the port that your Flask app will listen on
EXPOSE 5000

# Set environment variables for your Flask application
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PROCESSED_VIDEO_DIR=processed_videos

# Define the command to run your Flask application using Gunicorn
# 'app:app' refers to the Flask instance named 'app' in 'app.py'
# -w 2: run with 2 worker processes
# --timeout 120: set worker timeout to 120 seconds for long video processing
# -b 0.0.0.0:5000: bind to all network interfaces on port 5000
CMD ["gunicorn", "-w", "2", "--timeout", "120", "-b", "0.0.0.0:5000", "app:app"]