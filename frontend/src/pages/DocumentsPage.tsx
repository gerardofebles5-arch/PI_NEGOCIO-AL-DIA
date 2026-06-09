import { useEffect, useRef, useState } from "react";
import { api, type DocumentItem } from "../api";
import { CameraCapture } from "../components/CameraCapture";
import { DocumentDetailModal } from "../components/DocumentDetailModal";
import { formatBytes, formatDate, kindLabel } from "../utils";

const KIND_ICON: Record<string, string> = {
  pdf: "📄",
  image: "🖼️",
  docx: "📝",
  pptx: "📊",
  sheet: "📈",
  text: "🗒️",
  other: "📁",
};

export function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [camera, setCamera] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = async () => {
    setLoading(true);
    try {
      setDocs(await api.listDocuments());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, []);

  const uploadFiles = async (files: FileList | File[], source: string) => {
    setError("");
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await api.uploadDocument(file, source);
      }
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setUploading(false);
    }
  };

  const onCapture = async (file: File) => {
    setCamera(false);
    await uploadFiles([file], "camera");
  };

  const remove = async (id: number) => {
    if (!confirm("¿Eliminar este documento?")) return;
    try {
      await api.deleteDocument(id);
      setDocs((d) => d.filter((x) => x.id !== id));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-pi-ink">Documentos</h1>
        <p className="text-sm text-pi-ink-soft">
          Sube archivos o escanea con la cámara. Extraemos y archivamos la información.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-pi-brown/30 bg-pi-brown/10 px-3 py-2 text-sm text-pi-brown">
          {error}
        </div>
      )}

      {/* Uploader */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files, "upload");
        }}
        className="rounded-2xl border-2 border-dashed border-pi-gold-deep/30 bg-white/60 p-8 text-center"
      >
        <div className="font-display text-2xl text-pi-ink">
          Arrastra tus archivos aquí
        </div>
        <p className="mt-1 text-sm text-pi-ink-soft">
          PDF, imágenes, Word, Excel, PowerPoint o texto.
        </p>
        <div className="mt-4 flex flex-wrap justify-center gap-3">
          <button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            className="rounded-lg bg-pi-gold px-5 py-2.5 text-sm font-medium text-white transition hover:bg-pi-gold-deep disabled:opacity-60"
          >
            {uploading ? "Procesando…" : "Subir archivo"}
          </button>
          <button
            onClick={() => setCamera(true)}
            disabled={uploading}
            className="rounded-lg border border-pi-gold-deep/40 px-5 py-2.5 text-sm font-medium text-pi-ink transition hover:bg-pi-cream/60 disabled:opacity-60"
          >
            📷 Escanear con cámara
          </button>
        </div>
        <input
          ref={fileRef}
          type="file"
          multiple
          className="hidden"
          accept=".pdf,.png,.jpg,.jpeg,.gif,.bmp,.tiff,.webp,.docx,.doc,.pptx,.ppt,.xlsx,.xls,.csv,.txt,.md,image/*"
          onChange={(e) => {
            if (e.target.files?.length) uploadFiles(e.target.files, "upload");
            e.target.value = "";
          }}
        />
      </div>

      {/* List */}
      <div className="rounded-2xl border border-pi-gold-deep/15 bg-white">
        {loading ? (
          <div className="p-6 text-sm text-pi-ink-soft">Cargando…</div>
        ) : docs.length === 0 ? (
          <div className="p-8 text-center text-sm text-pi-ink-soft">
            Todavía no hay documentos. ¡Sube o escanea el primero!
          </div>
        ) : (
          <ul className="divide-y divide-pi-gold-deep/10">
            {docs.map((d) => (
              <li
                key={d.id}
                className="flex items-center gap-3 px-4 py-3 transition hover:bg-pi-cream/30"
              >
                <span className="text-2xl">{KIND_ICON[d.kind] || "📁"}</span>
                <button
                  onClick={() => setSelected(d.id)}
                  className="min-w-0 flex-1 text-left"
                >
                  <div className="truncate font-medium text-pi-ink">{d.filename}</div>
                  <div className="text-xs text-pi-ink-soft">
                    {kindLabel(d.kind)} · {formatBytes(d.size_bytes)} ·{" "}
                    {formatDate(d.created_at)}
                    {d.status === "failed" && (
                      <span className="ml-2 text-pi-brown">· error</span>
                    )}
                  </div>
                </button>
                <button
                  onClick={() => setSelected(d.id)}
                  className="hidden rounded-lg border border-pi-gold-deep/30 px-3 py-1.5 text-xs text-pi-ink-soft hover:bg-pi-cream/60 sm:block"
                >
                  Ver datos
                </button>
                <button
                  onClick={() => remove(d.id)}
                  className="rounded-lg px-2 py-1.5 text-xs text-pi-brown hover:bg-pi-brown/10"
                >
                  Eliminar
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {camera && <CameraCapture onCapture={onCapture} onClose={() => setCamera(false)} />}
      {selected !== null && (
        <DocumentDetailModal id={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}
