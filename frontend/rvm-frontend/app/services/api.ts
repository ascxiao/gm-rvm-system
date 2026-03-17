// app/services/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SystemStatus {
  state: "idle" | "scanning" | "valid_item" | "invalid_item";
  item_detected: string | null;
  confidence: number;
  error_message: string | null;
}

async function handleResponse(response: Response) {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error: ${response.status} - ${errorText}`);
  }
  return response.json();
}

export async function getStatus(): Promise<SystemStatus> {
  try {
    const response = await fetch(`${API_URL}/api/status`, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });
    return await handleResponse(response);
  } catch (error) {
    if (error instanceof Error && error.name === "TypeError") {
      throw new Error(
        "Cannot connect to backend. Make sure it's running on port 8000.",
      );
    }
    throw error;
  }
}

export async function triggerScan(): Promise<SystemStatus> {
  try {
    console.log("[API] Sending POST request to /api/scan");
    const response = await fetch(`${API_URL}/api/scan`, {
      method: "POST",
      signal: AbortSignal.timeout(10000), // 10 second timeout for scan
    });
    const result = await handleResponse(response);
    console.log("[API] Scan response received:", result);
    return result;
  } catch (error) {
    console.error("[API] triggerScan error:", error);
    if (error instanceof Error && error.name === "TypeError") {
      throw new Error(
        "Cannot connect to backend. Make sure it's running on port 8000.",
      );
    }
    throw error;
  }
}

export async function confirmItem(): Promise<SystemStatus> {
  try {
    const response = await fetch(`${API_URL}/api/confirm`, {
      method: "POST",
      signal: AbortSignal.timeout(5000),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error instanceof Error && error.name === "TypeError") {
      throw new Error(
        "Cannot connect to backend. Make sure it's running on port 8000.",
      );
    }
    throw error;
  }
}

export async function invalidItemRemoved(): Promise<SystemStatus> {
  try {
    const response = await fetch(`${API_URL}/api/invalid-item-removed`, {
      method: "POST",
      signal: AbortSignal.timeout(5000),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error instanceof Error && error.name === "TypeError") {
      throw new Error(
        "Cannot connect to backend. Make sure it's running on port 8000.",
      );
    }
    throw error;
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/api/health`, {
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function triggerArduino(): Promise<{
  success: boolean;
  message: string;
  trapdoor_triggered: boolean;
  coupon_triggered: boolean;
  arduino_status: {
    connected: boolean;
    trapdoor_open: boolean;
    coupon_printed: boolean;
  };
  timestamp: string;
}> {
  try {
    const response = await fetch(`${API_URL}/api/trigger-arduino`, {
      method: "POST",
      signal: AbortSignal.timeout(5000),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error instanceof Error && error.name === "TypeError") {
      throw new Error("Cannot connect to backend.");
    }
    throw error;
  }
}
