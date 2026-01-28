import { useEffect, useRef } from "react"

const Webcam = () => {
  const streamRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });

        if (streamRef.current) {
          streamRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error(err);
      }
    };

    startCamera();
  }, []);

  return (
    <>
      <video
        ref={streamRef}
        autoPlay
        playsInline
        className="w-full h-[70vh] object-cover rounded-lg"
      />
    </>
  );
};

export default Webcam