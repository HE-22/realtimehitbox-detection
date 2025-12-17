// Types for the API response
export interface Detection {
  id: number;
  class: string;
  confidence: number;
  polygon: number[][]; // Array of [x, y] points, normalized 0-1
}

export interface SegmentationResponse {
  detections: Detection[];
}

/**
 * Checks if a point (touch event) is inside a hitbox polygon.
 * Uses the Ray Casting algorithm.
 * 
 * @param point - The {x, y} coordinates of the user's tap (normalized 0-1)
 * @param polygon - The list of points from the API response
 */
export function isPointInPolygon(point: {x: number, y: number}, polygon: number[][]): boolean {
  let inside = false;
  const { x, y } = point;
  
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const xi = polygon[i][0], yi = polygon[i][1];
    const xj = polygon[j][0], yj = polygon[j][1];
    
    const intersect = ((yi > y) !== (yj > y)) &&
      (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      
    if (intersect) inside = !inside;
  }
  
  return inside;
}

/**
 * Example usage function to call your API
 */
export async function checkHit(imageUri: string, tapX: number, tapY: number, screenWidth: number, screenHeight: number) {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'photo.jpg',
  } as any);

  try {
    const response = await fetch('https://9f8fd2d58106.ngrok-free.app/segment/json', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const data: SegmentationResponse = await response.json();
    
    // Normalize the tap coordinates to 0-1 range to match the API
    const normalizedTap = {
      x: tapX / screenWidth,
      y: tapY / screenHeight
    };

    // Check if any person was hit
    for (const detection of data.detections) {
      if (isPointInPolygon(normalizedTap, detection.polygon)) {
        return { hit: true, confidence: detection.confidence };
      }
    }
    
    return { hit: false };
    
  } catch (error) {
    console.error("Hitbox check failed:", error);
    return { hit: false, error: true };
  }
}










