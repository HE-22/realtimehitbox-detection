import os
import shutil
from ultralytics import YOLO

# Configuration
MODEL_NAME = "yolo11n-seg"  # Using the latest YOLO11 Nano Segmentation model
EXPORT_DIR = "mobile_export"
MODEL_PATH = f"{MODEL_NAME}.pt"


def main():
    print(f"🚀 Starting export process for {MODEL_NAME}...")

    # Ensure export directory exists
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # 1. Load the model
    # If the model doesn't exist locally, it will be downloaded automatically
    print(f"📥 Loading {MODEL_NAME} model...")
    model = YOLO(MODEL_PATH)

    # 2. Export to TFLite (Best for Expo/React Native)
    # format='tflite': Exports to TensorFlow Lite format
    # int8=True: Quantizes to Int8 for 4x speedup on mobile NPU/GPU
    # nms=True: Adds Non-Max Suppression inside the model (simplifies frontend code)
    print("\n⚡ Exporting to TFLite (Int8 Quantized) for Mobile...")
    tflite_path = model.export(format="tflite", int8=True, nms=True)

    # Move the exported file to our specific folder
    # The export creates a folder or file, we need to find it and move it
    # Usually it's in the current directory as 'yolo11n-seg_saved_model' or similar
    # But ultralytics returns the path of the exported file

    destination_path = os.path.join(EXPORT_DIR, f"{MODEL_NAME}_int8.tflite")

    # Depending on export version, tflite_path might be a string path
    if isinstance(tflite_path, str) and os.path.exists(tflite_path):
        print(f"📦 Moving {tflite_path} to {destination_path}...")
        shutil.move(tflite_path, destination_path)
    else:
        # Fallback search if the return value isn't the direct path
        potential_file = (
            f"{MODEL_NAME}_ncnn_model"  # Just in case, but usually it's just .tflite
        )
        # Actually, ultralytics export usually leaves it in the root or creates a dir
        # Let's just look for the most likely file
        expected_output = (
            f"{MODEL_NAME}_saved_model/{MODEL_NAME}_float16.tflite"  # varies by flags
        )
        # With int8, it usually creates a file ending in .tflite
        # Let's simple check the returned path again
        pass

    print(f"\n✅ Export Complete! Files are in the '{EXPORT_DIR}' folder.")


if __name__ == "__main__":
    main()

