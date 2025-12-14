from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import Response
import uvicorn
from ultralytics import YOLO
import cv2
import numpy as np
import torch
import io
import time
import os

app = FastAPI()

# --- API Security ---
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # 1. Get key from environment (set this in Render Dashboard)
    expected_key = os.getenv("API_KEY")
    
    # 2. If no key is set in Render, allow everyone (Dev mode)
    if not expected_key:
        return True

    # 3. If key is set, check if header matches
    if api_key_header == expected_key:
        return True
    
    raise HTTPException(
        status_code=403,
        detail="Could not validate credentials"
    )

@app.get("/")
def read_root():
    return {"status": "online", "message": "Hitbox Detection API is running"}


# Global model variable
model = None


@app.on_event("startup")
def load_model():
    global model
    # Initialize model (same logic as before)
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print(f"Loading YOLOv8-seg model on {device}...")
    model = YOLO("yolov8n-seg.pt")
    model.to(device)
    print("Model loaded successfully.")


@app.post("/segment/image")
async def segment_image(file: UploadFile = File(...), authorized: bool = Depends(get_api_key)):
    """
    Accepts an image file, runs segmentation, and returns the annotated image.
    """
    # Read image file
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Run inference
    start_time = time.time()
    results = model(frame, classes=[0], verbose=False)  # 0 = person
    inference_time = (time.time() - start_time) * 1000
    print(f"Inference time: {inference_time:.2f} ms")

    # Get annotated frame
    annotated_frame = results[0].plot()

    # Encode back to jpg
    _, buffer = cv2.imencode(".jpg", annotated_frame)

    return Response(content=buffer.tobytes(), media_type="image/jpeg")


@app.post("/segment/json")
async def segment_json(file: UploadFile = File(...), authorized: bool = Depends(get_api_key)):
    """
    Returns the segmentation masks/polygons as JSON data (for hitboxes).
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    start_time = time.time()
    results = model(frame, classes=[0], verbose=False)
    inference_time = (time.time() - start_time) * 1000
    print(f"Inference time (JSON): {inference_time:.2f} ms")

    result = results[0]

    output = []
    if result.masks:
        # Get polygons (normalized coordinates 0-1)
        for i, seg in enumerate(result.masks.xyn):
            output.append(
                {
                    "id": i,
                    "class": "person",
                    "confidence": float(result.boxes.conf[i]),
                    "polygon": seg.tolist(),  # List of [x, y] points
                }
            )

    return {"detections": output}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
