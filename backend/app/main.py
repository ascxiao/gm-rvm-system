"""Main FastAPI application for Reverse Vending Machine."""
import logging
import cv2
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from app.models import StatusResponse, ScanResponse, ConfirmResponse, State
from app.services import StateManager
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reverse Vending Machine",
    description="Backend API for AI-powered reverse vending machine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state_manager = StateManager()

frontend_path = Path(__file__).parent.parent.parent / "frontend"

@app.get("/")
def read_root():
    """Serve the frontend HTML."""
    return FileResponse(str(frontend_path / "index.html"))

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutdown event received")
    state_manager.shutdown()


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "reverse-vending-machine-backend",
    }


@app.get("/api/status", response_model=StatusResponse)
def get_status():
    """Get current system status."""
    state = state_manager.get_status()
    return state.to_dict()


@app.get("/api/video-feed")
async def video_feed():
    """Stream live camera feed with YOLO detection overlay."""
    def generate():
        cap = cv2.VideoCapture(0)
        
        # Get the AI model from state_manager
        model = state_manager.ai.model
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Run YOLO detection on frame
                if model:
                    results = model.predict(source=frame, conf=0.25, verbose=False)
                    if results and len(results) > 0:
                        frame = results[0].plot()  # Draw bounding boxes
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                    
                frame_bytes = buffer.tobytes()
                
                # Yield frame in multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        finally:
            cap.release()
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.post("/api/scan", response_model=ScanResponse)
def start_scan():
    """Start scanning for an item."""
    state = state_manager.get_status()

    if state.state != State.IDLE:
        logger.warning(f"Scan requested while in {state.state.value} state")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot scan when in {state.state.value} state",
        )

    result = state_manager.start_scan()

    if result.state == State.VALID_ITEM:
        logger.info("Valid item detected")
        return ScanResponse(
            success=True,
            state=result.state.value,
            item_detected=result.item_detected,
            confidence=result.confidence,
            message="Water bottle detected! Trapdoor opening...",
        )

    logger.info("Invalid item detected")
    return ScanResponse(
        success=False,
        state=result.state.value,
        item_detected=result.item_detected,
        confidence=result.confidence,
        message=result.error_message or "Invalid item detected.",
    )


@app.post("/api/confirm", response_model=ConfirmResponse)
def confirm_drop():
    """Confirm item drop and complete the transaction."""
    state = state_manager.get_status()

    if state.state != State.VALID_ITEM:
        logger.warning(f"Confirm requested while in {state.state.value} state")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot confirm when in {state.state.value} state",
        )

    result = state_manager.confirm_drop()
    logger.info("Valid item confirmed, transaction completed")

    return ConfirmResponse(
        success=True,
        state=result.state.value,
        message="Item accepted. Thank you for recycling.",
    )


@app.post("/api/invalid-item-removed", response_model=StatusResponse)
def invalid_item_removed():
    """Handle removal of invalid item."""
    state = state_manager.get_status()

    if state.state != State.INVALID_ITEM:
        logger.warning(
            f"Invalid-item removal requested while in {state.state.value} state"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Cannot handle removal when in {state.state.value} state",
        )

    result = state_manager.handle_invalid_removal()
    logger.info("Invalid item removed, returning to IDLE")

    return StatusResponse(
        state=result.state.value,
        item_detected=result.item_detected,
        confidence=result.confidence,
        error_message=result.error_message,
    )


@app.post("/api/reset", response_model=StatusResponse)
def reset_system():
    """Emergency reset."""
    logger.warning("Emergency reset requested")
    result = state_manager.reset()

    return StatusResponse(
        state=result.state.value,
        item_detected=result.item_detected,
        confidence=result.confidence,
        error_message=result.error_message,
    )