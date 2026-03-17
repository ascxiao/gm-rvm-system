from ultralytics import YOLO
import cv2
import time
import torch
import sys
from pathlib import Path

# Determine best model path
AI_ROOT = Path(__file__).parent.parent
TRAINED_MODEL = AI_ROOT / "runs" / "detect" / "train" / "weights" / "best.pt"
MODEL_PATH = str(TRAINED_MODEL) if TRAINED_MODEL.exists() else str(AI_ROOT / "yolo11n.pt")
CONFIDENCE_THRESHOLD = 0.25  # Match backend threshold
DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

def main():
    print(f"\n🚀 Loading model from {MODEL_PATH} on device: {DEVICE}")
    model = YOLO(MODEL_PATH)
    model.to(DEVICE)

    # Use camera device 0 (same as backend for shared camera access)
    cap = cv2.VideoCapture(0)  

    if not cap.isOpened():
        print("❌ Cannot access webcam. Make sure it's connected or permissions are allowed.")
        print("   Note: If backend is running, it may be using the camera.")
        return

    prev_time = 0
    print("\n🎥 Starting real-time detection... Press 'ESC' to quit.\n")
    print("💡 This window shows the same AI detection used by the frontend.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame capture failed, exiting.")
            break

        # Run inference (same as backend)
        results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        annotated_frame = results[0].plot()

        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        # Add FPS counter
        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        
        # Add detection info
        if results[0].boxes and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            conf_idx = boxes.conf.argmax()
            detected_class = results[0].names[int(boxes.cls[conf_idx])]
            confidence = float(boxes.conf[conf_idx])
            
            cv2.putText(
                annotated_frame,
                f"Detected: {detected_class} ({confidence:.2%})",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
        
        cv2.imshow("YOLO Bottle Detection (Frontend Compatible)", annotated_frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Detection ended. Webcam released.\n")


if __name__ == "__main__":
    main()