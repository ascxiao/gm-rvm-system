from ultralytics import YOLO
import cv2
import time
import torch

MODEL_PATH = "runs/detect/train/weights/best.pt" 
CONFIDENCE_THRESHOLD = 0.5                        
DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

def main():
    print(f"\n🚀 Loading model from {MODEL_PATH} on device: {DEVICE}")
    model = YOLO(MODEL_PATH)
    model.to(DEVICE)

    cap = cv2.VideoCapture(0)  

    if not cap.isOpened():
        print("❌ Cannot access webcam. Make sure it's connected or permissions are allowed.")
        return

    prev_time = 0
    print("\n🎥 Starting real-time detection... Press 'ESC' to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame capture failed, exiting.")
            break

        results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        annotated_frame = results[0].plot()

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.2f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.imshow("YOLO11n Bottle Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Detection ended. Webcam released.\n")


if __name__ == "__main__":
    main()