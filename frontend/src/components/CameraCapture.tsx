import { useEffect, useRef, useState } from "react";

interface Props {
  onCapture: (file: File) => void;
  onClose: () => void;
}

export function CameraCapture({ onCapture, onClose }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let active = true;
    async function start() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" } },
          audio: false,
        });
        if (!active) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
          setReady(true);
        }
      } catch (e) {
        setError(
          "No se pudo acceder a la cámara. Revisa los permisos o usa 'Subir archivo'. (" +
            (e as Error).message +
            ")",
        );
      }
    }
    start();
    return () => {
      active = false;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const snap = () => {
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], `escaneo-${Date.now()}.jpg`, {
          type: "image/jpeg",
        });
        onCapture(file);
      },
      "image/jpeg",
      0.92,
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-black/95 p-4">
      <div className="flex items-center justify-between text-pi-cream">
        <span className="font-display text-xl">Escanear con la cámara</span>
        <button
          onClick={onClose}
          className="rounded-lg border border-pi-cream/30 px-3 py-1.5 text-sm"
        >
          Cerrar
        </button>
      </div>

      <div className="flex flex-1 items-center justify-center">
        {error ? (
          <p className="max-w-md text-center text-pi-cream/80">{error}</p>
        ) : (
          <video
            ref={videoRef}
            playsInline
            muted
            className="max-h-[70vh] w-full max-w-2xl rounded-2xl object-contain"
          />
        )}
      </div>

      {!error && (
        <div className="flex justify-center py-4">
          <button
            onClick={snap}
            disabled={!ready}
            className="h-16 w-16 rounded-full border-4 border-pi-cream bg-pi-gold disabled:opacity-50"
            aria-label="Capturar"
          />
        </div>
      )}
    </div>
  );
}
