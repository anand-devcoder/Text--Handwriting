# -------------------------------
# Base image  (THIS WORKS)
# -------------------------------
FROM python:3.11-bookworm

# -------------------------------
# Environment variables
# -------------------------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# -------------------------------
# Install system dependencies
# -------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Create app directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Copy project files
# -------------------------------
COPY . /app

# -------------------------------
# Upgrade pip and install Python dependencies
# -------------------------------
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Expose port (optional)
# -------------------------------
EXPOSE 10000

# -------------------------------
# Run the app with Gunicorn using Render's PORT env
# -------------------------------
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]

