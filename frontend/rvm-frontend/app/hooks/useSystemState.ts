"use client";

import { useState, useEffect } from "react";
import {
  getStatus,
  triggerScan,
  confirmItem,
  invalidItemRemoved,
  checkBackendHealth,
} from "@/app/services/api";
import type { SystemStatus } from "@/app/services/api";

export function useSystemState() {
  const [status, setStatus] = useState<SystemStatus>({
    state: "idle",
    item_detected: null,
    confidence: 0,
    error_message: null,
  });
  const [loading, setLoading] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string>("");

  const fetchStatus = async () => {
    try {
      const data = await getStatus();
      console.log("[useSystemState] fetchStatus received:", data);
      setStatus(data);
      setBackendConnected(true);
      setConnectionError("");
    } catch (error) {
      console.error("[useSystemState] Failed to fetch status:", error);
      setBackendConnected(false);
      if (error instanceof Error) {
        setConnectionError(error.message);
      }
    }
  };

  const scan = async () => {
    console.log("[useSystemState] scan() called");
    setLoading(true);
    try {
      console.log("[useSystemState] Calling triggerScan API...");
      const scanResult = await triggerScan();
      console.log("[useSystemState] triggerScan API completed:", scanResult);

      // Poll status until scanning completes
      let attempts = 0;
      const interval = setInterval(async () => {
        try {
          console.log("[useSystemState] Polling status, attempt:", attempts);
          const data = await getStatus();
          console.log("[useSystemState] Poll result:", data);
          setStatus(data);
          if (data.state !== "scanning" || attempts++ > 20) {
            console.log(
              "[useSystemState] Scan polling complete, state:",
              data.state,
            );
            clearInterval(interval);
            setLoading(false);
          }
        } catch (pollError) {
          console.error("[useSystemState] Error during polling:", pollError);
          clearInterval(interval);
          setLoading(false);
        }
      }, 500);
    } catch (error) {
      console.error("[useSystemState] Scan failed:", error);
      if (error instanceof Error) {
        console.error("[useSystemState] Error message:", error.message);
      }
      setLoading(false);
    }
  };

  const confirm = async () => {
    console.log("[useSystemState] confirm() called");
    try {
      console.log("[useSystemState] Calling confirmItem API...");
      await confirmItem();
      console.log("[useSystemState] confirmItem API completed");
      await fetchStatus();
    } catch (error) {
      console.error("[useSystemState] Confirm failed:", error);
    }
  };

  const removeInvalidItem = async () => {
    console.log("[useSystemState] removeInvalidItem() called");
    try {
      console.log("[useSystemState] Calling invalidItemRemoved API...");
      await invalidItemRemoved();
      console.log("[useSystemState] invalidItemRemoved API completed");
      await fetchStatus();
    } catch (error) {
      console.error("[useSystemState] Remove invalid item failed:", error);
    }
  };

  useEffect(() => {
    console.log("[useSystemState] Hook mounted, checking backend health");

    // Check backend health first
    checkBackendHealth().then((isHealthy) => {
      if (isHealthy) {
        console.log(
          "[useSystemState] Backend is healthy, starting status polling",
        );
        fetchStatus(); // Initial fetch
      } else {
        console.warn("[useSystemState] Backend is not responding");
        setBackendConnected(false);
        setConnectionError(
          "Backend server is not running. Start it with: cd backend && python main.py",
        );
      }
    });

    const interval = setInterval(fetchStatus, 2000); // Poll every 2 seconds
    console.log("[useSystemState] Started polling interval (2s)");
    return () => {
      console.log("[useSystemState] Cleaning up polling interval");
      clearInterval(interval);
    };
  }, []);

  return {
    status,
    loading,
    scan,
    confirm,
    removeInvalidItem,
    backendConnected,
    connectionError,
  };
}
