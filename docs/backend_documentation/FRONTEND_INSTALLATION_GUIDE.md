# Frontend Installation Guide

## Setup Backend Locally

### 1. Create Virtual Environment

**Windows:**
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Server

```bash
python main.py
```

Verify with: `curl http://localhost:8000/api/health`

---

## Backend State Machine

```
IDLE ──[POST /scan]──→ SCANNING
                           │
                    ┌──────┴──────┐
                    │             │
              ✓ VALID_ITEM    ✗ INVALID_ITEM
                    │             │
              [POST /confirm] [POST /invalid-item-removed]
                    │             │
                    └──────┬──────┘
                           ↓
                         IDLE
```

**Frontend per state:**
- **IDLE**: Show "Scan" button
- **SCANNING**: Show loader
- **VALID_ITEM**: Confirm after ~5 sec
- **INVALID_ITEM**: Prompt user to remove item

---

## API Endpoints

### GET /api/status
Get current state anytime.

```bash
curl http://localhost:8000/api/status
```

Response:
```json
{
  "state": "idle",
  "item_detected": null,
  "confidence": 0.0,
  "error_message": null
}
```

---

### POST /api/scan
Trigger detection. **Only works in IDLE.**

```bash
curl -X POST http://localhost:8000/api/scan
```

Success:
```json
{
  "success": true,
  "state": "valid_item",
  "item_detected": "bottle",
  "confidence": > 3.0
}
```

Failure:
```json
{
  "success": false,
  "state": "invalid_item",
  "item_detected": "cup",
  "confidence": < 3.0
}
```

---

### POST /api/confirm
Accept bottle. **Only works in VALID_ITEM.** Logs to CSV.

```bash
curl -X POST http://localhost:8000/api/confirm
```

Response:
```json
{
  "state": "idle",
  "message": "Bottle accepted and logged"
}
```

---

### POST /api/invalid-item-removed
Reject item. **Only works in INVALID_ITEM.**

```bash
curl -X POST http://localhost:8000/api/invalid-item-removed
```

Response:
```json
{
  "state": "idle",
  "message": "Invalid item removed"
}
```

---

### GET /api/video-feed
MJPEG stream with overlay.

```html
<img src="http://localhost:8000/api/video-feed" alt="Feed" />
```

---

### POST /api/reset
Emergency reset to IDLE.

```bash
curl -X POST http://localhost:8000/api/reset
```

---

## Frontend Integration

**Set `.env.local`:**
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Main Flow (pages/scan/page.tsx)

```typescript
'use client';
import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function ScanPage() {
  const router = useRouter();
  const hasRunRef = useRef(false);

  useEffect(() => {
    if (hasRunRef.current) return;
    hasRunRef.current = true;

    const runScan = async () => {
      try {
        // Call /api/scan - only works in IDLE state
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/scan`, {
          method: 'POST',
        });
        const data = await res.json();

        if (!res.ok) {
          // HTTP 400/500 - show error page
          router.push('/scan/fail');
          return;
        }

        // data.success = true → VALID_ITEM state (bottle detected)
        // data.success = false → INVALID_ITEM state (wrong item)
        if (data.success) {
          // Bottle detected - wait 5s then call /api/confirm
          setTimeout(async () => {
            await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/confirm`, {
              method: 'POST',
            });
            // Backend logs to CSV, transitions to IDLE
            router.push('/scan/success');
          }, 5000);
        } else {
          // Wrong item detected
          router.push('/scan/fail');
        }
      } catch (error) {
        console.error('Scan failed:', error);
        router.push('/scan/fail');
      }
    };

    runScan();
  }, [router]);

  return <div>Scanning...</div>;
}
```

### Poll Status (optional, pages/status/page.tsx)

Get current state without triggering scan:
```typescript
useEffect(() => {
  const pollStatus = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/status`);
    const data = await res.json();
    console.log('Current state:', data.state);
    // data.state = "idle" | "scanning" | "valid_item" | "invalid_item" | "printing"
  };
  const interval = setInterval(pollStatus, 1000);
  return () => clearInterval(interval);
}, []);
```

### Invalid Item Handling (pages/scan/fail/page.tsx)

When detection fails (invalid item), call this after user removes it:
```typescript
const handleItemRemoved = async () => {
  await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/invalid-item-removed`, {
    method: 'POST',
  });
  // Returns to IDLE - ready for next scan
  router.push('/');
};
```

### Emergency Recovery (any page)

If stuck in bad state:
```typescript
const handleReset = async () => {
  await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/reset`, {
    method: 'POST',
  });
  // Forces back to IDLE
};
```

---

## Error Handling

**HTTP 400** - State violation (e.g., can't scan when scanning)
- Show error, wait, retry

**HTTP 500** - Server error
- Show "Connection lost"
- Optionally call `POST /api/reset`

---

## Testing

**Interactive docs:** `http://localhost:8000/docs`

**Quick curl tests:**
```bash
curl http://localhost:8000/api/status
curl -X POST http://localhost:8000/api/scan
curl -X POST http://localhost:8000/api/confirm
curl -X POST http://localhost:8000/api/reset
```

---

## Troubleshooting

**Backend not responding:**
```bash
curl http://localhost:8000/api/health
# If fails, restart: cd backend && python main.py
```

**Port 8000 in use:**
```bash
# Windows
Get-Process -Name python | Stop-Process

# Mac/Linux
lsof -i :8000 && kill -9 <PID>
```

**Camera permission denied:**
- Windows: Settings → Privacy → Camera
- Mac: System Settings → Privacy & Security → Camera
- Linux: `sudo usermod -a -G video $USER`

**Detection fails:**
- Check camera: `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`
- Check model: `ai/yolo11n.pt` exists
- Check logs: `backend/app/logs/`

---

See [BACKEND_DOCUMENTATION.md](./BACKEND_DOCUMENTATION.md) for details.