"use client";

import { useEffect, useRef, useState } from "react";

interface CameraPreviewProps {
  isOpen: boolean;
  onClose: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function CameraPreview({ isOpen, onClose }: CameraPreviewProps) {
  const imgRef = useRef<HTMLImageElement>(null);
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    setIsLoading(true);
    setError("");

    const videoFeedUrl = `${API_URL}/api/video-feed`;
    console.log(
      "[CameraPreview] Loading video feed from backend:",
      videoFeedUrl,
    );

    // Set up the image source to display the MJPEG stream
    if (imgRef.current) {
      imgRef.current.src = videoFeedUrl;
      imgRef.current.onload = () => {
        setIsLoading(false);
        console.log("[CameraPreview] Video feed connected");
      };
      imgRef.current.onerror = () => {
        setError(
          "Failed to connect to camera feed. Ensure backend is running.",
        );
        setIsLoading(false);
        console.error("[CameraPreview] Video feed error");
      };
    }

    return () => {
      // Clean up the image source
      if (imgRef.current) {
        imgRef.current.src = "";
        console.log("[CameraPreview] Video feed stopped");
      }
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg overflow-hidden max-w-2xl w-full">
        <div className="bg-gray-900 relative">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-10">
              <div className="text-white text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent mb-4 mx-auto"></div>
                <p>Starting camera...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-90 z-10">
              <div className="text-white text-center p-6">
                <p className="text-xl font-bold mb-2">⚠️ Camera Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          <img
            ref={imgRef}
            alt="Camera feed with AI detection"
            className="w-full aspect-video bg-black object-contain"
          />

          <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-1 rounded text-sm font-bold">
            🤖 AI DETECTION
          </div>
        </div>

        <div className="bg-gray-100 p-4 flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-500 text-white rounded-lg font-bold hover:bg-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
