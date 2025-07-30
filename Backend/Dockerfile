# Use a minimal base image
FROM python:3.10-slim as base

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install essential dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install only essential Python deps
COPY requirements.txt .

# Install requirements WITHOUT cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Expose Flask port
EXPOSE 5000

# Run using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
