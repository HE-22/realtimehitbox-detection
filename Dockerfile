# Use an official lightweight Python image
FROM python:3.9-slim

# Install system dependencies required for OpenCV
# libgl1-mesa-glx is needed for cv2
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY api.py .
# We also need the model file. 
# Ideally, we download it during build or at startup to keep image small, 
# but copying it is faster for now if it exists locally.
# If it doesn't exist, the code will download it on startup.
COPY yolov8n-seg.pt . 

# Expose the port
EXPOSE 8000

# Command to run the application
CMD sh -c "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"

