# Base image
FROM python:3.11-slim

# Install system packages including Tesseract OCR and dependencies for Pillow, OpenCV, ReportLab
RUN apt-get update && apt-get install -y \
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
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip first
RUN python3 -m pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 10000

# Start the app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
