# Use lightweight Python image
FROM python:3.10-slim

# Avoid prompts and speed up installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port (Railway will auto-use this)
EXPOSE 5000

# Run with Gunicorn (recommended for production)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
