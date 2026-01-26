"""TEST-ONLY: Camera test with real-time YOLO detection visualization."""
import cv2
import logging
from pathlib import Path
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run live camera feed with YOLO detection overlay."""
    logger.info("Starting YOLO camera test")

    ai_root = Path(__file__).parent.parent / "ai"
    best_model = ai_root / "runs" / "detect" / "train" / "weights" / "best.pt"

    if best_model.exists():
        model_path = str(best_model)
        logger.info(f"Using trained model: {model_path}")
    else:
        model_path = "yolo11n.pt"
        logger.warning("Trained model not found, using pretrained model")

    try:
        model = YOLO(model_path)
        logger.info("YOLO model loaded successfully")
    except Exception:
        logger.exception("Failed to load YOLO model")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Could not open camera")
        return

    logger.info("Camera opened (press 'q' to quit)")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read frame from camera")
                break

            results = model.predict(source=frame, conf=0.5, verbose=False)

            if results and len(results) > 0:
                annotated_frame = results[0].plot()
                cv2.imshow("YOLO Detection (TEST)", annotated_frame)
            else:
                cv2.imshow("YOLO Detection (TEST)", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                logger.info("Exit requested by user")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera released, test ended")


if __name__ == "__main__":
    main()