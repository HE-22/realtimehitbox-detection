import cv2
from ultralytics import YOLO
import torch
import time
import sys

class RealTimeSegmenter:
    def __init__(self, model_path='yolov8n-seg.pt'):
        """
        Initialize the YOLOv8 segmentation model.
        Auto-selects Apple Silicon (MPS), CUDA, or CPU.
        """
        # Check for MPS (Apple Silicon) or CUDA
        if torch.backends.mps.is_available():
            self.device = 'mps'
        elif torch.cuda.is_available():
            self.device = 'cuda'
        else:
            self.device = 'cpu'
            
        print(f"Loading YOLOv8 model on device: {self.device}")
        
        # Load the model (will download automatically if not present)
        self.model = YOLO(model_path)
        # Move to device explicitly
        self.model.to(self.device)

    def process_image(self, image_path):
        """
        Process a single image and return the segmented result.
        """
        print(f"Processing image: {image_path}")
        start_time = time.time()
        
        # Read image
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"Error: Could not read image {image_path}")
            return

        # Inference with class filtering (0 = person)
        results = self.model(frame, classes=[0], verbose=False)
        process_time = (time.time() - start_time) * 1000
        
        print(f"Processing time: {process_time:.1f}ms")
        
        # Show result
        annotated_frame = results[0].plot()
        cv2.imshow('Person Segmentation Result', annotated_frame)
        print("Press any key to close the image window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run_webcam(self):
        """
        Run real-time inference on webcam stream.
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return

        print("Starting webcam... Press 'q' to quit.")
        
        fps_start_time = time.time()
        frame_count = 0
        fps = 0
        
        while True:
            success, frame = cap.read()
            if not success:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            
            # Run inference
            # classes=[0] ensures we only look for people
            results = self.model(frame, classes=[0], verbose=False)
            
            # Visualize results
            # plot() returns a numpy array of the annotated image
            annotated_frame = results[0].plot()
            
            # Calculate FPS
            frame_count += 1
            if time.time() - fps_start_time >= 1.0:
                fps = frame_count / (time.time() - fps_start_time)
                frame_count = 0
                fps_start_time = time.time()
            
            # Display FPS on frame
            cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('YOLOv8 Real-Time Person Segmentation', annotated_frame)
            
            # Break loop on 'q'
            if cv2.waitKey(1) == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    segmenter = RealTimeSegmenter()
    
    # Check if an image path was provided
    if len(sys.argv) > 1:
        segmenter.process_image(sys.argv[1])
    else:
        segmenter.run_webcam()

