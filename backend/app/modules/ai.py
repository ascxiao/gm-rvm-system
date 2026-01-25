"""Real AI inference using YOLO11n."""
import cv2
import logging
import threading
from pathlib import Path
from ultralytics import YOLO

logger = logging.getLogger(__name__)

BOTTLE_CONFIDENCE_THRESHOLD = 0.3


class RealAI:
    """YOLO-based object detection service."""

    def __init__(self, model_path: str = None):
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
        except Exception:
            self.model_loaded = False
            self.model = None
            logger.exception("Failed to load AI model")

        self.camera = None
        self.camera_device = 0
        self.camera_lock = threading.Lock()

    def get_camera(self):
        """Return a shared camera instance."""
        if self.camera is None or not self.camera.isOpened():
            logger.info("Opening camera")
            self.camera = cv2.VideoCapture(self.camera_device)
            if not self.camera.isOpened():
                logger.error("Failed to open camera")
                return None
        return self.camera

    def capture_frame(self):
        """Capture a single frame from the camera."""
        try:
            with self.camera_lock:
                cam = self.get_camera()
                if cam is None:
                    return None

                ret, frame = cam.read()
                if ret:
                    return frame

                logger.error("Failed to read frame from camera")
                return None
        except Exception:
            logger.exception("Camera capture error")
            return None

    def detect(self, source):
        """Run object detection using the camera or a provided frame."""
        if not self.model_loaded or self.model is None:
            logger.error("Model not loaded, skipping detection")
            return "unknown", 0.0

        try:
            if isinstance(source, int):
                frame = self.capture_frame()
                if frame is None:
                    logger.warning("Could not capture frame for detection")
                    return "unknown", 0.0
                source = frame

            results = self.model.predict(source=source, conf=0.25, verbose=False)

            if results:
                result = results[0]
                if result.boxes and len(result.boxes) > 0:
                    boxes = result.boxes
                    conf_idx = boxes.conf.argmax()

                    detected_class = result.names[int(boxes.cls[conf_idx])]
                    confidence = float(boxes.conf[conf_idx])

                    logger.info(
                        "Detected object: %s (confidence=%.2f)",
                        detected_class,
                        confidence,
                    )
                    return detected_class, round(confidence, 2)

            logger.info("No objects detected")
            return "unknown", 0.0

        except Exception:
            logger.exception("Inference error")
            return "unknown", 0.0

    def is_water_bottle(self, detected_class: str, confidence: float) -> bool:
        """Check if detection qualifies as a water bottle."""
        bottle_keywords = ["bottle", "water", "plastic"]
        is_bottle = any(kw in detected_class.lower() for kw in bottle_keywords)
        return is_bottle and confidence >= BOTTLE_CONFIDENCE_THRESHOLD

    def release_camera(self):
        """Release the camera resource."""
        if self.camera is not None:
            logger.info("Releasing camera")
            self.camera.release()
            self.camera = None