export const KIND_LABELS: Record<string, string> = {
  pdf: "PDF",
  image: "Imagen",
  docx: "Word",
  pptx: "Presentación",
  sheet: "Hoja de cálculo",
  text: "Texto",
  other: "Otro",
};

export const KIND_COLORS: Record<string, string> = {
  PDF: "#873c20",
  Imagenes: "#be882e",
  Imagen: "#be882e",
  Word: "#936a31",
  Presentaciones: "#d9b158",
  "Presentación": "#d9b158",
  "Hojas de calculo": "#ac7649",
  "Hoja de cálculo": "#ac7649",
  Texto: "#3e403d",
  Otros: "#512509",
  Otro: "#512509",
};

export function kindLabel(kind: string): string {
  return KIND_LABELS[kind] || kind;
}

export function formatBytes(bytes: number): string {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(i ? 1 : 0)} ${units[i]}`;
}

export function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString("es", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function formatAmount(value: number): string {
  return value.toLocaleString("es", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
