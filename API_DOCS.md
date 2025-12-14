# Hitbox Detection API Documentation

This API provides real-time person segmentation for the "Real-Life Call of Duty" game. It accepts images and returns either the segmented image or the hitbox polygons (JSON).

## Base URL
Local: `http://localhost:8000`
Ngrok: `https://<your-ngrok-id>.ngrok.io` (after running ngrok)

## Endpoints

### 1. Health Check
Check if the API is online.

- **URL:** `/`
- **Method:** `GET`

**Response:**
```json
{"status": "online", "message": "Hitbox Detection API is running"}
```

### 2. Get Hitbox Data (JSON)
Use this for the game logic to determine if a shot hit a player.

- **URL:** `/segment/json`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: The image file (jpg/png)

**Response:**
```json
{
  "detections": [
    {
      "id": 0,
      "class": "person",
      "confidence": 0.89,
      "polygon": [
        [0.12, 0.34],
        [0.15, 0.38],
        ...
      ]
    }
  ]
}
```
*Note: Polygon coordinates are normalized (0.0 to 1.0) relative to image width/height.*

### 2. Get Visual Mask (Image)
Use this for debugging or visualizing what the server sees.

- **URL:** `/segment/image`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: The image file (jpg/png)

**Response:**
- Returns a `image/jpeg` with the segmentation mask overlay.

---

## How to Run

### 1. Start Server
```bash
python api.py
```

### 2. Expose via Ngrok
In a separate terminal:
```bash
ngrok http 8000
```
Copy the `https` forwarding URL provided by ngrok.

### 3. Test with Curl
Replace `<ngrok-url>` with your actual URL.

**Test JSON:**
```bash
curl -X POST -F "file=@/path/to/image.jpg" "<ngrok-url>/segment/json"
```

**Test Image:**
```bash
curl -X POST -F "file=@/path/to/image.jpg" "<ngrok-url>/segment/image" --output result.jpg
```

