import { useEffect, useState } from "react";
import { api, type DocumentDetail } from "../api";
import { formatAmount, formatBytes, formatDate, kindLabel } from "../utils";

function Chips({ title, items }: { title: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wider text-pi-gold-deep">
        {title}
      </div>
      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {items.map((it) => (
          <span
            key={it}
            className="rounded-full bg-pi-cream/60 px-2.5 py-1 text-xs text-pi-ink"
          >
            {it}
          </span>
        ))}
      </div>
    </div>
  );
}

export function DocumentDetailModal({
  id,
  onClose,
}: {
  id: number;
  onClose: () => void;
}) {
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getDocument(id).then(setDoc).catch((e) => setError((e as Error).message));
  }, [id]);

  const fields = doc?.extraction?.fields;

  return (
    <div
      className="fixed inset-0 z-40 flex items-end justify-center bg-black/50 p-0 sm:items-center sm:p-6"
      onClick={onClose}
    >
      <div
        className="scroll-thin max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-t-2xl bg-white p-6 sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {error && <div className="text-pi-brown">{error}</div>}
        {!doc && !error && <div className="text-pi-ink-soft">Cargando…</div>}
        {doc && (
          <>
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="font-display text-2xl text-pi-ink">{doc.filename}</h3>
                <p className="text-xs text-pi-ink-soft">
                  {kindLabel(doc.kind)} · {formatBytes(doc.size_bytes)} ·{" "}
                  {doc.source === "camera" ? "Cámara" : "Subido"} ·{" "}
                  {formatDate(doc.created_at)}
                </p>
                {doc.owner_email && (
                  <p className="text-xs text-pi-gold-deep">Propietario: {doc.owner_email}</p>
                )}
              </div>
              <button
                onClick={onClose}
                className="rounded-lg border border-pi-gold-deep/30 px-3 py-1.5 text-sm"
              >
                Cerrar
              </button>
            </div>

            {doc.status === "failed" && (
              <div className="mt-4 rounded-lg bg-pi-brown/10 px-3 py-2 text-sm text-pi-brown">
                No se pudo procesar: {doc.error}
              </div>
            )}

            {fields && (
              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                {fields.total_amount > 0 && (
                  <div className="rounded-xl bg-pi-ink p-4 text-pi-cream sm:col-span-2">
                    <div className="text-xs uppercase tracking-wide text-pi-cream/70">
                      Suma de montos detectados
                    </div>
                    <div className="font-display text-3xl">
                      {formatAmount(fields.total_amount)}
                    </div>
                    {Object.keys(fields.currencies).length > 0 && (
                      <div className="mt-1 text-sm text-pi-cream/80">
                        {Object.entries(fields.currencies)
                          .map(([c, v]) => `${formatAmount(v)} ${c}`)
                          .join(" · ")}
                      </div>
                    )}
                  </div>
                )}
                <Chips title="Correos" items={fields.emails} />
                <Chips title="Teléfonos" items={fields.phones} />
                <Chips title="Fechas" items={fields.dates} />
                <Chips title="RIF / Identificadores" items={fields.rifs} />
                {fields.keywords.length > 0 && (
                  <div className="sm:col-span-2">
                    <Chips
                      title="Palabras clave"
                      items={fields.keywords.map(([w, c]) => `${w} (${c})`)}
                    />
                  </div>
                )}
              </div>
            )}

            {doc.extraction && (
              <div className="mt-5">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-medium uppercase tracking-wider text-pi-gold-deep">
                    Texto extraído ({doc.extraction.word_count} palabras)
                  </div>
                  <a
                    href={`/api/documents/${doc.id}/file`}
                    className="text-xs text-pi-gold-deep hover:underline"
                  >
                    Descargar original
                  </a>
                </div>
                <pre className="scroll-thin mt-2 max-h-64 overflow-auto whitespace-pre-wrap rounded-xl bg-pi-cream/30 p-3 text-xs text-pi-ink-soft">
                  {doc.extraction.raw_text || "(Sin texto extraído)"}
                </pre>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
