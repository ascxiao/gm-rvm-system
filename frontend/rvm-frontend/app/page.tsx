"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { useSystemState } from "@/app/hooks/useSystemState";
import { triggerArduino } from "@/app/services/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const router = useRouter();
  const {
    status,
    scan,
    confirm,
    removeInvalidItem,
    backendConnected,
    connectionError,
  } = useSystemState();
  const [hasScanned, setHasScanned] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isOnScanScreen, setIsOnScanScreen] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const [cameraError, setCameraError] = useState<string>("");

  // Load AI detection feed from backend
  useEffect(() => {
    if (isOnScanScreen || !backendConnected) return;

    const videoFeedUrl = `${API_URL}/api/video-feed`;
    console.log(
      "[HomePage] Loading AI detection feed from backend:",
      videoFeedUrl,
    );

    if (imgRef.current) {
      imgRef.current.src = videoFeedUrl;
      imgRef.current.onload = () => {
        console.log("[HomePage] AI detection feed connected");
        setCameraError("");
      };
      imgRef.current.onerror = () => {
        setCameraError("AI detection feed unavailable");
        console.error("[HomePage] AI detection feed error");
      };
    }

    return () => {
      if (imgRef.current) {
        imgRef.current.src = "";
        console.log("[HomePage] AI detection feed stopped");
      }
    };
  }, [isOnScanScreen, backendConnected]);

  useEffect(() => {
    console.log("[HomePage] Status updated:", {
      state: status.state,
      item_detected: status.item_detected,
      hasScanned,
    });

    // Trigger scan when transitioning to scan screen if in idle state
    if (isOnScanScreen && status.state === "idle" && !hasScanned) {
      console.log(
        "[HomePage] Status is idle and hasn't scanned, triggering scan...",
      );
      scan();
      setHasScanned(true);
    }
  }, [status.state, scan, hasScanned, isOnScanScreen]);

  const handleScanClick = () => {
    console.log("[HomePage] Scan button clicked");
    setIsOnScanScreen(true);
    setHasScanned(false);
  };

  const handleConfirmSuccess = async () => {
    console.log("[HomePage] Confirm button clicked");
    setIsProcessing(true);
    try {
      console.log("[HomePage] Calling confirm() - This will:");
      console.log("  🚪 Close the trapdoor");
      console.log("  🎟️  Send coupon print signal");
      await confirm();
      console.log("✅ [HomePage] Confirm completed - Arduino signals sent!");

      console.log("[HomePage] Waiting before reset");
      setTimeout(() => {
        console.log("[HomePage] Resetting to home screen");
        setIsOnScanScreen(false);
        setHasScanned(false);
        setIsProcessing(false);
      }, 1000);
    } catch (error) {
      console.error("[HomePage] Error during confirm:", error);
      setIsProcessing(false);
    }
  };

  const handleRemoveItem = async () => {
    console.log("[HomePage] Remove button clicked");
    console.log("[HomePage] Calling removeInvalidItem()");
    setIsProcessing(true);
    try {
      await removeInvalidItem();
      console.log("[HomePage] removeInvalidItem() completed successfully");
      console.log("[HomePage] Waiting 1 second before reset");
      setTimeout(() => {
        console.log("[HomePage] Resetting to home screen");
        setIsOnScanScreen(false);
        setHasScanned(false);
        setIsProcessing(false);
      }, 1000);
    } catch (error) {
      console.error("[HomePage] Error during remove:", error);
      setIsProcessing(false);
    }
  };

  // SCANNING STATE
  if (isOnScanScreen && status.state === "scanning") {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-200 gap-8 font-sans">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#078C10] border-t-gray-200" />
        <div className="flex flex-col items-center text-[#078C10]">
          <span className="animate-bounce font-bold">Scanning...</span>
          <span className="text-xs mt-8">Property of Green Module Systems</span>
        </div>
      </div>
    );
  }

  // SUCCESS STATE
  if (isOnScanScreen && status.state === "valid_item") {
    return (
      <div className="flex min-h-screen items-center justify-center font-sans text-[#3B9549]">
        <main className="flex min-h-screen w-full max-w-3xl flex-col p-8 bg-gray-200 gap-8 items-center justify-center ">
          <div className="flex rounded-4xl bg-[#3B9549] px-6 pt-10 overflow-hidden w-[40vh] h-[50vh] justify-center">
            <div className="flex rounded-t-3xl justify-center pt-6 pb-4 bg-[#114e1a] w-full h-full">
              <Image
                src="/images/Bottle.png"
                alt="Bottle"
                width={160}
                height={220}
                className="object-contain"
              />
            </div>
          </div>
          <span className="font-bold text-xl">SUCCESSFUL!</span>
          <span className="font-bold text-xl animate-pulse">
            Printing coupon...
          </span>
          <div className="text-center mt-4">
            <p className="text-sm text-[#114E1A]">
              Item: <strong>{status.item_detected}</strong>
            </p>
            <p className="text-sm text-[#114E1A]">
              Confidence:{" "}
              <strong>{(status.confidence * 100).toFixed(1)}%</strong>
            </p>
          </div>
          <button
            onClick={handleConfirmSuccess}
            disabled={isProcessing}
            className="px-6 py-2 bg-[#3B9549] text-white rounded-lg font-bold hover:bg-[#2d6f36] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? "Processing..." : "Confirm"}
          </button>
          <span className="text-xs mt-2">Property of Green Module Systems</span>
        </main>
      </div>
    );
  }

  // FAIL STATE
  if (isOnScanScreen && status.state === "invalid_item") {
    return (
      <div className="flex min-h-screen items-center justify-center font-sans text-[#8C0707]">
        <main className="flex min-h-screen w-full max-w-3xl flex-col p-8 bg-gray-200 gap-8 items-center justify-center ">
          <div className="flex rounded-4xl bg-[#C80B0E] px-6 pt-10 overflow-hidden w-[40vh] h-[50vh] justify-end">
            <Image
              src="/images/error.png"
              alt="Error"
              width={60}
              height={60}
              className="absolute"
            />
            <div className="flex rounded-t-3xl justify-center pt-6 pb-4 bg-[#4E1112] w-full h-full">
              <Image
                src="/images/failed.png"
                alt="Failed"
                width={160}
                height={220}
                className="object-contain"
              />
            </div>
          </div>
          <div className="flex flex-col text-center justify-center">
            <span className="font-bold text-xl">FAILED!</span>
            <span className="font-medium text-md">
              Please put only 500ml plastic bottles
            </span>

            <span className="font-bold text-xl mt-2">
              Please remove item from compartment
            </span>
          </div>

          <button
            onClick={handleRemoveItem}
            disabled={isProcessing}
            className="px-6 py-2 bg-[#C80B0E] text-white rounded-lg font-bold hover:bg-[#a30809] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isProcessing ? "Processing..." : "Item Removed"}
          </button>

          <span className="text-xs mt-2">Property of Green Module Systems</span>
        </main>
      </div>
    );
  }

  // IDLE/LOADING STATE (on scan screen but not yet scanning)
  if (isOnScanScreen && status.state === "idle") {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-200 gap-8 font-sans">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#078C10] border-t-gray-200" />
        <div className="flex flex-col items-center text-[#078C10]">
          <span className="animate-bounce font-bold">Loading...</span>
          <span className="text-xs mt-8">Property of Green Module Systems</span>
        </div>
      </div>
    );
  }

  // HOME SCREEN (initial state)
  return (
    <div className="flex min-h-screen items-center justify-center font-sans">
      <main className="flex min-h-screen w-full max-w-3xl flex-col p-8 bg-gray-200 gap-3">
        {/* Backend Connection Status */}
        {!backendConnected && (
          <div className="bg-red-100 border-2 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-2">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-500"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-bold">Backend Not Connected</h3>
                <p className="text-xs mt-1">{connectionError}</p>
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-row justify-center gap-3">
          <div className="flex justify-center rounded-4xl bg-[#3B9549] overflow-hidden w-full h-[35vh] relative">
            {/* Backend status badge */}
            <div
              className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-bold z-10 ${
                backendConnected
                  ? "bg-green-500 text-white"
                  : "bg-red-500 text-white"
              }`}
            >
              {backendConnected ? "● CONNECTED" : "● OFFLINE"}
            </div>

            {!backendConnected ? (
              <div className="flex flex-col items-center justify-center text-white text-center p-4">
                <p className="text-3xl mb-2">📹</p>
                <p className="text-sm">AI Detection Offline</p>
                <p className="text-xs mt-2">
                  Start backend to see live detection
                </p>
              </div>
            ) : cameraError ? (
              <div className="flex flex-col items-center justify-center text-white text-center">
                <p className="text-sm mb-2">⚠️</p>
                <p className="text-xs">{cameraError}</p>
              </div>
            ) : (
              <img
                ref={imgRef}
                alt="AI Detection Feed with Bounding Boxes"
                className="w-full h-full object-cover"
              />
            )}
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-2">
          <div className="flex flex-col text-[#114E1A] text-center border-2 p-3 rounded-3xl justify-center gap-2">
            <h2 className="font-bold">PUT BOTTLE INSIDE COMPARTMENT</h2>
            <hr />
            <p className="text-xs">One bottle at a time</p>
          </div>

          <div className="flex flex-col text-[#114E1A] text-center border-2 p-3 rounded-3xl ustify-center gap-2">
            <p className="text-[3vh] font-medium">
              Note: Only 500ml plastic bottles are accepted
            </p>
            <p className="text-[2vh]">Property of Green Module Systems</p>
          </div>
        </div>

        <button
          onClick={handleScanClick}
          disabled={!backendConnected}
          className="w-full p-4 bg-[#078C10] rounded-4xl font-extrabold text-xl text-white hover:bg-[#056b0a] disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {backendConnected ? "SCAN BOTTLE" : "BACKEND OFFLINE - CANNOT SCAN"}
        </button>
      </main>
    </div>
  );
}
