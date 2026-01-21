"""Real AI inference using YOLO11n."""
import cv2
import logging
from pathlib import Path
from ultralytics import YOLO

logger = logging.getLogger(__name__)

BOTTLE_CONFIDENCE_THRESHOLD = 0.3


class RealAI:
    """YOLO-based object detection service."""

    def __init__(self, model_path: str = None):
        """Load YOLO model from trained weights or fallback."""
        logger.info("Initializing AI module")

        if model_path is None:
            ai_root = Path(__file__).parent.parent.parent.parent / "ai"
            best_model = ai_root / "runs" / "detect" / "train" / "weights" / "best.pt"

            if best_model.exists():
                model_path = str(best_model)
                logger.info("Using trained YOLO model")
            else:
                model_path = "yolo11n.pt"
                logger.warning("Trained model not found, using pretrained model")

        try:
            self.model = YOLO(model_path)
            self.model_loaded = True
            logger.info("AI model loaded successfully")
        except Exception as e:
            self.model_loaded = False
            self.model = None
            logger.exception("Failed to load AI model")

    def capture_frame(self, camera_device: int = 0):
        """Capture a single frame from the specified camera device."""
        try:
            cap = cv2.VideoCapture(camera_device)
            if not cap.isOpened():
                logger.error("Failed to open camera")
                return None

            ret, frame = cap.read()
            cap.release()

            if ret:
                return frame

            logger.error("Failed to read frame from camera")
            return None
        except Exception:
            logger.exception("Camera capture error")
            return None

    def detect(self, source):
        """Run object detection on a frame or camera source."""
        if not self.model_loaded or self.model is None:
            logger.error("Model not loaded, skipping detection")
            return "unknown", 0.0

        try:
            if isinstance(source, int):
                frame = self.capture_frame(source)
                if frame is None:
                    return "unknown", 0.0
                source = frame

            results = self.model.predict(source=source, conf=0.25, verbose=False)

            if results and len(results) > 0:
                result = results[0]
                if len(result.boxes) > 0:
                    boxes = result.boxes
                    conf_idx = boxes.conf.argmax()

                    detected_class = result.names[int(boxes.cls[conf_idx])]
                    confidence = float(boxes.conf[conf_idx])

                    logger.info(
                        f"Detected object: {detected_class} (confidence={confidence:.2f})"
                    )
                    return detected_class, round(confidence, 2)

            logger.info("No objects detected")
            return "unknown", 0.0

        except Exception:
            logger.exception("Inference error")
            return "unknown", 0.0

    def is_water_bottle(self, detected_class: str, confidence: float) -> bool:
        """Determine whether the detection qualifies as a water bottle."""
        bottle_keywords = ["bottle", "water", "plastic"]
        is_bottle = any(kw in detected_class.lower() for kw in bottle_keywords)
        is_confident = confidence >= BOTTLE_CONFIDENCE_THRESHOLD
        return is_bottle and is_confident