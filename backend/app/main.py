"""Main FastAPI application for Reverse Vending Machine."""
import logging
import asyncio
import cv2
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.models import StatusResponse, ScanResponse, ConfirmResponse, State
from app.services import StateManager

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state_manager = StateManager()


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutdown event received")
    state_manager.shutdown()


@app.get("/api/video-feed")
async def video_feed():
    """Stream live camera feed with YOLO detection overlay using shared camera."""
    async def generate():
        camera = state_manager.ai.get_camera()
        model = state_manager.ai.model
        frame_skip = 0
        
        if camera is None:
            logger.error("Could not access shared camera for video feed")
            yield b''
            return
        
        try:
            while True:
                with state_manager.ai.camera_lock:
                    ret, frame = camera.read()
                
                if not ret:
                    logger.warning("Failed to read frame in video stream")
                    state_manager.ai.release_camera()
                    camera = state_manager.ai.get_camera()
                    if camera is None:
                        break
                    continue
        
                frame_skip += 1
                if frame_skip % 2 == 0:
                    if model:
                        try:
                            results = model.predict(source=frame, conf=0.25, verbose=False)
                            if results and len(results) > 0:
                                frame = results[0].plot()
                        except Exception as e:
                            logger.error(f"Error in YOLO prediction: {e}")
                
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not ret:
                    continue
                    
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
                await asyncio.sleep(0.01)
        
        except GeneratorExit:
            logger.info("Video stream client disconnected")
        except Exception as e:
            logger.exception("Error in video feed generation")
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


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


@app.post("/api/scan", response_model=ScanResponse)
def start_scan():
    """Start scanning for an item (NO PRINTING HERE)."""
    logger.info("\n" + "="*60)
    logger.info("🔍 SCAN REQUEST RECEIVED")
    logger.info("="*60)

    state = state_manager.get_status()
    logger.info(f"Current state: {state.state.value}")

    if state.state != State.IDLE:
        logger.warning(f"❌ Scan requested while in {state.state.value} state")
        raise HTTPException(
            status_code=400,
            detail=f"Cannot scan when in {state.state.value} state",
        )

    logger.info("Starting scan detection...")
    result = state_manager.start_scan()
    logger.info(f"Scan completed. Result state: {result.state.value}")

    if result.state == State.VALID_ITEM:
        logger.info("✅ Valid item detected")
        logger.info(f"📦 Detected: {result.item_detected} ({result.confidence:.2%})")
        logger.info("="*60 + "\n")

        return ScanResponse(
            success=True,
            state=result.state.value,
            item_detected=result.item_detected,
            confidence=result.confidence,
            message="Water bottle detected! Please confirm to complete.",
        )

    logger.warning("❌ Invalid item detected")
    logger.info("="*60 + "\n")

    return ScanResponse(
        success=False,
        state=result.state.value,
        item_detected=result.item_detected,
        confidence=result.confidence,
        message=result.error_message or "Invalid item detected.",
    )

@app.post("/api/confirm", response_model=ConfirmResponse)
def confirm_drop():
    """Confirm item drop and complete transaction (PRINTS ONCE)."""
    state = state_manager.get_status()

    # Idempotent safety: if already processed, do NOT print again
    if state.state != State.VALID_ITEM:
        logger.info(f"Confirm called while in {state.state.value} state - no action")
        return ConfirmResponse(
            success=True,
            state=state.state.value,
            message="Item already processed.",
        )

    logger.info("🎟️ Processing confirm - closing trapdoor...")
    result = state_manager.confirm_drop()
    logger.info("✅ Valid item confirmed, transaction completed")

    # ✅ PRINT ONLY HERE
    try:
        from app.modules.printer import print_receipt
        import random, string
        coupon_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Use ANSI escape codes for bold text (if supported by printer)
        bold_on = '\033[1m'
        bold_off = '\033[0m'
        receipt_text = (
            "================================\n"
            "      RECYCLING RECEIPT\n"
            "================================\n"
            f"Item: {state.item_detected}\n"
            f"Confidence: {state.confidence:.2%}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "--------------------------------\n"
            "Coupon Code:\n"
            f"{bold_on}{coupon_code}{bold_off}\n"
            "--------------------------------\n"
            "Thank you for recycling!\n"
            "\n"
        )
        if print_receipt(receipt_text):
            logger.info("📠 Receipt sent to printer successfully")
        else:
            logger.warning("⚠️ Failed to print receipt")

    except Exception as e:
        logger.error(f"Printing failed on confirm: {e}")

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
        # If already idle or other state, just return ok (idempotent)
        logger.info(
            f"Invalid-item removal called while in {state.state.value} state - returning ok"
        )
        return StatusResponse(
            state=state.state.value,
            item_detected=state.item_detected,
            confidence=state.confidence,
        )

    result = state_manager.handle_invalid_removal()
    logger.info("Invalid item removed, returning to IDLE")

    return StatusResponse(
        state=result.state.value,
        item_detected=result.item_detected,
        confidence=result.confidence,
        error_message=result.error_message,
    )


@app.post("/api/trigger-arduino")
def trigger_arduino():
    """Dummy endpoint to test Arduino signal triggering."""
    logger.info("🤖 ARDUINO TEST ENDPOINT CALLED")
    logger.info("   Note: In production, trapdoor opens on scan, coupon prints on confirm")
    
    # Get current arduino status for testing
    arduino_status = state_manager.arduino.get_status()
    
    return {
        "success": True,
        "message": "Arduino status retrieved (test endpoint)",
        "note": "Trapdoor opens automatically on valid scan. Coupon prints on confirm.",
        "arduino_status": arduino_status,
        "timestamp": datetime.now().isoformat(),
    }


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