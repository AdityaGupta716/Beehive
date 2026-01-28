import { useEffect, useRef, useState } from "react";
import { CameraIcon, XMarkIcon, ArrowPathIcon, CheckIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

interface WebcamProps {
  onCapture: (file: File) => void;
  onClose?: () => void;
}

const Webcam = ({ onCapture, onClose }: WebcamProps) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1920 }, height: { ideal: 1080 } },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsCameraActive(true);
    } catch (err) {
      console.error("Camera error:", err);
      const errorMessage =
        err instanceof Error
          ? err.name === "NotAllowedError"
            ? "Camera permission denied. Please allow camera access."
            : err.name === "NotFoundError"
              ? "No camera found on this device."
              : "Failed to access camera."
          : "Failed to access camera.";
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) {
      toast.error("Camera not ready");
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!context) {
      toast.error("Failed to capture photo");
      return;
    }

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob and then to file
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          toast.error("Failed to capture photo");
          return;
        }

        const timestamp = new Date().getTime();
        const file = new File([blob], `webcam-capture-${timestamp}.png`, {
          type: "image/png",
        });

        // Stop camera and show preview
        stopCamera();
        const imageUrl = URL.createObjectURL(blob);
        setCapturedImage(imageUrl);
        setCapturedFile(file);
        toast.success("Photo captured!");
      },
      "image/png",
      0.95
    );
  };

  const handleRetake = () => {
    // Clean up the captured image
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage);
    }
    setCapturedImage(null);
    setCapturedFile(null);
    // Restart camera
    startCamera();
  };

  const handleSubmit = () => {
    if (capturedFile) {
      onCapture(capturedFile);
      // Clean up
      if (capturedImage) {
        URL.revokeObjectURL(capturedImage);
      }
      toast.success("Photo ready to upload!");
    }
  };

  // Auto-start camera on mount
  useEffect(() => {
    startCamera();

    // Cleanup on unmount
    return () => {
      stopCamera();
      if (capturedImage) {
        URL.revokeObjectURL(capturedImage);
      }
    };
  }, []);

  const handleClose = () => {
    stopCamera();
    if (capturedImage) {
      URL.revokeObjectURL(capturedImage);
    }
    onClose?.();
  };

  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center">
      {/* Video Feed or Captured Image */}
      {capturedImage ? (
        <img
          src={capturedImage}
          alt="Captured"
          className="w-full h-[70vh] object-cover rounded-lg"
        />
      ) : (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-[70vh] object-cover rounded-lg"
        />
      )}

      {/* Hidden canvas for capturing */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Error Message */}
      {error && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg text-center max-w-md z-20">
          <p className="font-semibold mb-2">Camera Error</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={handleClose}
            className="mt-4 px-4 py-2 bg-white text-red-500 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Close
          </button>
        </div>
      )}

      {/* Camera Controls - Capture Button */}
      {isCameraActive && !error && !capturedImage && (
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex items-center gap-4">
          <button
            onClick={capturePhoto}
            className="w-16 h-16 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-all transform hover:scale-105 flex items-center justify-center"
            title="Capture Photo"
          >
            <div className="w-14 h-14 bg-yellow-400 rounded-full flex items-center justify-center">
              <CameraIcon className="h-8 w-8 text-black" />
            </div>
          </button>
        </div>
      )}

      {/* Preview Controls - Retake and Submit Buttons */}
      {capturedImage && (
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex items-center gap-4">
          {/* Retake Button */}
          <button
            onClick={handleRetake}
            className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors shadow-lg"
            title="Retake Photo"
          >
            <ArrowPathIcon className="h-5 w-5" />
            <span>Retake</span>
          </button>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            className="flex items-center gap-2 bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 px-6 rounded-lg transition-colors shadow-lg"
            title="Submit Photo"
          >
            <CheckIcon className="h-5 w-5" />
            <span>Submit</span>
          </button>
        </div>
      )}

      {/* Close Button */}
      {onClose && (
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 bg-white rounded-full text-black shadow-lg hover:bg-gray-100 transition-colors z-10"
          title="Close Camera"
        >
          <XMarkIcon className="h-6 w-6" />
        </button>
      )}

      {/* Start Camera Button */}
      {!isCameraActive && !error && !capturedImage && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <button
            onClick={startCamera}
            className="flex items-center gap-2 bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 px-6 rounded-lg transition-colors shadow-lg"
          >
            <CameraIcon className="h-6 w-6" />
            <span>Start Camera</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default Webcam;