from ultralytics import YOLO
import cv2
import os

# Paths
MODEL_PATH = "mobile_export/yolo11n-seg_int8.tflite"
IMAGE_PATH = "running_test.jpg"


def main():
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    print(f"Loading TFLite model: {MODEL_PATH}...")
    # Ultralytics can load TFLite models directly!
    model = YOLO(MODEL_PATH, task="segment")

    print(f"Running inference on {IMAGE_PATH} (Looking for PERSON only)...")
    # Run prediction
    # classes=[0] filters for 'person' class only (COCO dataset class 0 is person)
    results = model(IMAGE_PATH, classes=[0])

    # Display results
    for result in results:
        # result.plot() creates the image with boxes/masks drawn
        # boxes=True draws the bounding box (hitbox)
        # masks=True draws the segmentation mask (precise shape)
        annotated_frame = result.plot(boxes=True, masks=True)

        output_filename = "person_hitbox_test.jpg"

        # Save using cv2 (since plot returns a numpy array)
        cv2.imwrite(output_filename, annotated_frame)
        print(f"✅ Hitbox image saved to {output_filename}")

        # Print detection info
        print(f"Found {len(result.boxes)} persons:")
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            name = result.names[cls_id]
            print(f" - {name} ({conf:.2f})")


if __name__ == "__main__":
    main()
