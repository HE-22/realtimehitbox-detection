# Hitbox Detection API Documentation

This API provides real-time person segmentation for the "Real-Life Call of Duty" game. It accepts images and returns either the segmented image or the hitbox polygons (JSON).

It is hosted on **Google Cloud Run** for high-performance inference with scale-to-zero capabilities.

## Base URL
**Public Server:** `https://hitbox-api-165369327789.us-central1.run.app`

*(Old Render URL: `https://realtimehitbox-detection.onrender.com`)*

## Authentication
The public server may require an API Key to prevent abuse.
- **Header:** `x-api-key`
- **Value:** *(Set this in Google Cloud Run Environment Variables)*

*(If no key is set, the API is public).*

## Deployment (Google Cloud Run)
To deploy updates to this service, use the Google Cloud CLI.

```bash
# 1. Build and push the image (Architecture: Linux/AMD64)
gcloud builds submit --tag us-central1-docker.pkg.dev/experiments-475114/hitbox-repo/hitbox-api .

# 2. Deploy to Cloud Run (High Performance)
# 4 vCPU, 4GB RAM, Max Concurrency 8, Min Instances 0 (Scale to Zero)
gcloud run deploy hitbox-api \
    --image us-central1-docker.pkg.dev/experiments-475114/hitbox-repo/hitbox-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8000 \
    --memory 4Gi \
    --cpu 4 \
    --concurrency 8 \
    --min-instances 0 \
    --max-instances 10
```

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

### 3. Get Visual Mask (Image)
Use this for debugging or visualizing what the server sees.

- **URL:** `/segment/image`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: The image file (jpg/png)

**Response:**
- Returns a `image/jpeg` with the segmentation mask overlay.

---

## Code Examples

### TypeScript / JavaScript (Frontend)
```typescript
/**
 * Sends an image to the Hitbox API and gets back polygons.
 */
export async function getHitboxes(imageFile: File) {
  const formData = new FormData();
  formData.append("file", imageFile);

  const API_URL = "https://hitbox-api-165369327789.us-central1.run.app";
  // const API_KEY = "YOUR_KEY_HERE"; // Uncomment if you set a key

  try {
    const response = await fetch(`${API_URL}/segment/json`, {
      method: "POST",
      headers: {
        // "x-api-key": API_KEY, 
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.detections; // Returns list of polygons
  } catch (error) {
    console.error("Failed to get hitboxes:", error);
    return [];
  }
}
```

### Curl (Terminal)
**Test JSON:**
```bash
curl -X POST -F "file=@/path/to/image.jpg" https://hitbox-api-165369327789.us-central1.run.app/segment/json
```

**Test Image (Visual Debug):**
```bash
curl -X POST -F "file=@/path/to/image.jpg" https://hitbox-api-165369327789.us-central1.run.app/segment/image --output result.jpg
```
