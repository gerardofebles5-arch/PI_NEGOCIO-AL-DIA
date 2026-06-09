import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, type Dashboard } from "../api";
import { useAuth } from "../auth";
import { KIND_COLORS, formatAmount, formatDate, kindLabel } from "../utils";

function StatCard({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div
      className={`rounded-2xl border p-5 ${
        accent
          ? "border-transparent bg-pi-ink text-pi-cream"
          : "border-pi-gold-deep/15 bg-white"
      }`}
    >
      <div className={`text-xs uppercase tracking-wider ${accent ? "text-pi-cream/70" : "text-pi-gold-deep"}`}>
        {label}
      </div>
      <div className="mt-1 font-display text-3xl">{value}</div>
    </div>
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.dashboard().then(setData).catch((e) => setError((e as Error).message));
  }, []);

  if (error) return <div className="text-pi-brown">{error}</div>;
  if (!data) return <div className="text-pi-ink-soft">Cargando dashboard…</div>;

  const kindData = Object.entries(data.by_kind).map(([name, value]) => ({ name, value }));
  const keywordData = data.top_keywords.slice(0, 8).map(([name, value]) => ({ name, value }));
  const currencyEntries = Object.entries(data.currencies);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl text-pi-ink">
            Hola, {user?.name?.split(" ")[0] || "bienvenido"}
          </h1>
          <p className="text-sm text-pi-ink-soft">
            Resumen inteligente de tu información.
          </p>
        </div>
        <Link
          to="/documentos"
          className="rounded-lg bg-pi-gold px-4 py-2.5 text-sm font-medium text-white transition hover:bg-pi-gold-deep"
        >
          + Escanear / subir documento
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Documentos" value={String(data.total_documents)} accent />
        <StatCard label="Palabras extraídas" value={data.total_words.toLocaleString("es")} />
        <StatCard
          label="Montos detectados"
          value={data.total_amount ? formatAmount(data.total_amount) : "—"}
        />
        <StatCard label="Tipos distintos" value={String(Object.keys(data.by_kind).length)} />
      </div>

      {/* Insights */}
      <div className="rounded-2xl border border-pi-gold-deep/15 bg-gradient-to-br from-pi-cream/60 to-white p-5">
        <h2 className="font-display text-xl text-pi-ink">Lo que detectamos por ti</h2>
        <ul className="mt-3 space-y-2">
          {data.insights.map((ins, i) => (
            <li key={i} className="flex gap-2 text-sm text-pi-ink-soft">
              <span className="mt-0.5 text-pi-gold">◆</span>
              {ins}
            </li>
          ))}
        </ul>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-pi-gold-deep/15 bg-white p-5">
          <h2 className="font-display text-xl text-pi-ink">Documentos por tipo</h2>
          {kindData.length ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={kindData} dataKey="value" nameKey="name" outerRadius={90} label>
                  {kindData.map((entry) => (
                    <Cell key={entry.name} fill={KIND_COLORS[entry.name] || "#be882e"} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="mt-6 text-sm text-pi-ink-soft">Aún no hay datos.</p>
          )}
        </div>

        <div className="rounded-2xl border border-pi-gold-deep/15 bg-white p-5">
          <h2 className="font-display text-xl text-pi-ink">Temas recurrentes</h2>
          {keywordData.length ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={keywordData} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#be882e" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="mt-6 text-sm text-pi-ink-soft">Aún no hay datos.</p>
          )}
        </div>
      </div>

      {currencyEntries.length > 0 && (
        <div className="rounded-2xl border border-pi-gold-deep/15 bg-white p-5">
          <h2 className="font-display text-xl text-pi-ink">Montos por moneda</h2>
          <div className="mt-3 flex flex-wrap gap-3">
            {currencyEntries.map(([cur, val]) => (
              <div key={cur} className="rounded-xl bg-pi-cream/50 px-4 py-3">
                <div className="text-xs uppercase tracking-wide text-pi-gold-deep">{cur}</div>
                <div className="font-display text-2xl text-pi-ink">{formatAmount(val)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent */}
      <div className="rounded-2xl border border-pi-gold-deep/15 bg-white p-5">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-xl text-pi-ink">Documentos recientes</h2>
          <Link to="/documentos" className="text-sm text-pi-gold-deep hover:underline">
            Ver todos
          </Link>
        </div>
        {data.recent.length ? (
          <ul className="mt-3 divide-y divide-pi-gold-deep/10">
            {data.recent.map((d) => (
              <li key={d.id} className="flex items-center justify-between py-2.5 text-sm">
                <span className="truncate text-pi-ink">{d.filename}</span>
                <span className="ml-3 flex-none text-xs text-pi-ink-soft">
                  {kindLabel(d.kind)} · {formatDate(d.created_at)}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-pi-ink-soft">
            Aún no has subido documentos.
          </p>
        )}
      </div>
    </div>
  );
}
