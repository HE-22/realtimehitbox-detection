from ultralytics import YOLO

# Load your custom model (or the standard one)
model = YOLO("yolo11n-seg.pt")

# Export to CoreML format
# format='coreml': exports to Apple's .mlpackage format
# nms=True: adds post-processing (Non-Max Suppression) inside the model so you get clean results directly
# int8=True: (Optional) enables 8-bit quantization for faster speed on Neural Engine (might slightly reduce accuracy)
print("Exporting model to CoreML...")
model.export(format="coreml", nms=True)
print("Export complete! Look for 'yolov8n-seg.mlpackage' in your folder.")

