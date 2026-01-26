# Backend Documentation

Reverse vending machine backend API for bottle detection and processing.

### Prerequisites

- Python 3.12 (But theoretically, python 3.8+ works too)
- pip (Python package manager)
- Webcam connected to system

### Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend starts on `http://localhost:8000`

### Dependencies

Core packages:
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **ultralytics**: YOLO model and inference
- **pydantic**: Data validation
- **opencv-python**: Camera and image processing

See `requirements.txt` for full list.










## Quick Start

Start the backend:

```bash
cd backend
python main.py
```

Server runs on: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

Health check:
```bash
curl http://localhost:8000/api/health
```

## System Overview

The backend is a FastAPI application that manages:
- Bottle detection via YOLO computer vision
- State machine for system flow control
- Hardware control (trapdoor integration)
- CSV logging of accepted bottles
- MJPEG video streaming with detection overlay

## State Machine

The system operates on five discrete states:

- **IDLE**: Waiting for scan request
- **SCANNING**: Running YOLO detection (~2 seconds)
- **VALID_ITEM**: Bottle detected, trapdoor open
- **INVALID_ITEM**: Non-bottle detected
- **PRINTING**: Processing reward

State transitions:
```
IDLE → SCANNING → VALID_ITEM → IDLE
            ↓
        INVALID_ITEM → IDLE
```

All state transitions are validated. Invalid transitions return HTTP 400.

## API Endpoints

### GET /api/health
Health check endpoint.

Response (200 OK):
```json
{
  "status": "ok"
}
```

### GET /api/status
Returns current system state.

Response:
```json
{
  "state": "idle",
  "item_detected": null,
  "confidence": 0.0,
  "error_message": null
}
```

### POST /api/scan
Trigger YOLO detection. Only works when state is IDLE.

Response (200 OK - bottle detected):
```json
{
  "success": true,
  "state": "valid_item",
  "item_detected": "bottle",
  "confidence": 0.51,
  "message": "Water bottle detected! Trapdoor opening..."
}
```

Response (200 OK - invalid item):
```json
{
  "success": false,
  "state": "invalid_item",
  "item_detected": "unknown",
  "confidence": 0.0,
  "message": "Invalid item detected."
}
```

Error (400 Bad Request - wrong state):
```json
{
  "detail": "Cannot scan when in scanning state"
}
```

### POST /api/confirm
Accept and log the detected item. Only works when state is VALID_ITEM. Logs bottle to CSV.

Response:
```json
{
  "success": true,
  "state": "idle",
  "message": "Item accepted. Thank you for recycling."
}
```

### POST /api/invalid-item-removed
Reset system after invalid item removal. Only works when state is INVALID_ITEM.

Response:
```json
{
  "state": "idle",
  "item_detected": null,
  "confidence": 0.0,
  "error_message": null
}
```

### GET /api/video-feed (OPTIONAL)
MJPEG stream with YOLO detection overlay. 30fps with frame skipping.

Response: Live video stream (image/jpeg)

### POST /api/reset
Force state back to IDLE. Used for error recovery.

Response:
```json
{
  "state": "idle",
  "item_detected": null,
  "confidence": 0.0,
  "error_message": null
}
```

## Data Logging

Accepted bottles are logged to: `backend/app/logs/bottle_log_YYYYMMDD_HHMMSS.csv`

Columns:
- bottle_id: Unique identifier
- timestamp: When bottle was confirmed
- detected_class: YOLO detection class
- confidence: Detection confidence score (0.0-1.0)

Logging occurs only on POST /api/confirm, not on rejected items.

## Error Handling

All state transitions are validated. Invalid transitions return:

```json
{
  "detail": "Cannot scan when in scanning state"
}
```

HTTP 400 Bad Request indicates:
- Wrong state for operation
- Invalid state transition attempt

Clients should retry or call POST /api/reset to recover.

## Testing

Health check:
```bash
curl http://localhost:8000/api/health
```

Get status:
```bash
curl http://localhost:8000/api/status
```

Trigger scan (requires IDLE state):
```bash
curl -X POST http://localhost:8000/api/scan
```

Confirm bottle:
```bash
curl -X POST http://localhost:8000/api/confirm
```

Reset system:
```bash
curl -X POST http://localhost:8000/api/reset
```

View API docs in browser:
```
http://localhost:8000/docs
```

## Configuration

Key parameters can be adjusted in implementation files:

- **BOTTLE_CONFIDENCE_THRESHOLD**: Minimum detection confidence (default: 0.3)
- **camera_device**: Which camera input to use (default: 0)
- **Detection model**: Automatically uses trained model or falls back to pretrained YOLO11n
- **API port**: Configured in main.py (default: 8000)
- **CORS**: Enabled for all origins during development

## Performance Characteristics

- **Detection latency**: ~2 seconds per scan (YOLO inference)
- **API response time**: <100ms typical
- **Video stream**: 30fps MJPEG with frame skipping
- **Memory usage**: ~500MB (YOLO model + camera buffers)
- **Concurrent requests**: Safely handled with threading locks

## Backend Characteristics

**Concurrency**: The backend safely handles concurrent requests. Video streaming and scan operations can run simultaneously without conflicts.

**Model Selection**: Automatically attempts to load trained YOLO model. Falls back to pretrained model if not available. Both modes work correctly.

**Data Logging**: Accepted bottles are logged to CSV with timestamp and confidence score. Logging only occurs on confirmation, not on rejected scans.

**State Protection**: Every API endpoint validates current state before executing. Invalid state transitions are rejected with HTTP 400 errors.

**Camera Integration**: Supports any camera device accessible via OpenCV. Typically device 0 is the default webcam.

**Hardware Abstraction**: Trapdoor control via configurable hardware interface (MockArduino or real Arduino).