"""Main FastAPI application for Reverse Vending Machine."""
import logging
from fastapi import FastAPI, HTTPException
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

state_manager = StateManager()


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