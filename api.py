from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
import uvicorn
from ultralytics import YOLO
import cv2
import numpy as np
import torch
import io
import time

app = FastAPI()


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
async def segment_image(file: UploadFile = File(...)):
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
async def segment_json(file: UploadFile = File(...)):
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
