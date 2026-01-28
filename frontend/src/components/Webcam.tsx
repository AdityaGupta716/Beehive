import { useEffect, useRef } from "react"

const Webcam = () => {
  const camRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });

        if (camRef.current) {
          camRef.current.srcObject = stream;
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
        ref={camRef}
        autoPlay
        playsInline
        className="w-full h-[70vh] object-cover rounded-lg"
      />
    </>
  );
};

export default Webcam