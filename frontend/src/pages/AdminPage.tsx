import { useEffect, useState } from "react";
import { api, type DocumentDetail, type User } from "../api";
import { DocumentDetailModal } from "../components/DocumentDetailModal";
import { formatAmount, formatDate, kindLabel } from "../utils";

interface Stats {
  total_users: number;
  total_admins: number;
  total_documents: number;
  total_amount: number;
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-pi-gold-deep/15 bg-white p-5">
      <div className="text-xs uppercase tracking-wider text-pi-gold-deep">{label}</div>
      <div className="mt-1 font-display text-3xl text-pi-ink">{value}</div>
    </div>
  );
}

export function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [docs, setDocs] = useState<DocumentDetail[]>([]);
  const [tab, setTab] = useState<"users" | "docs">("users");
  const [selected, setSelected] = useState<number | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.adminStats(), api.adminUsers(), api.adminDocuments()])
      .then(([s, u, d]) => {
        setStats(s);
        setUsers(u);
        setDocs(d);
      })
      .catch((e) => setError((e as Error).message));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-pi-ink">Panel de administración</h1>
        <p className="text-sm text-pi-ink-soft">
          Acceso total a usuarios y documentos del sistema.
        </p>
      </div>

      {error && <div className="text-pi-brown">{error}</div>}

      {stats && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard label="Usuarios" value={String(stats.total_users)} />
          <StatCard label="Administradores" value={String(stats.total_admins)} />
          <StatCard label="Documentos" value={String(stats.total_documents)} />
          <StatCard
            label="Montos totales"
            value={stats.total_amount ? formatAmount(stats.total_amount) : "—"}
          />
        </div>
      )}

      <div className="flex gap-2">
        {(["users", "docs"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
              tab === t ? "bg-pi-gold text-white" : "bg-white text-pi-ink-soft border border-pi-gold-deep/20"
            }`}
          >
            {t === "users" ? "Usuarios" : "Documentos"}
          </button>
        ))}
      </div>

      {tab === "users" && (
        <div className="overflow-hidden rounded-2xl border border-pi-gold-deep/15 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-pi-cream/40 text-left text-xs uppercase tracking-wide text-pi-gold-deep">
              <tr>
                <th className="px-4 py-3">Usuario</th>
                <th className="px-4 py-3">Rol</th>
                <th className="px-4 py-3">Documentos</th>
                <th className="px-4 py-3">Registro</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-pi-gold-deep/10">
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="px-4 py-3">
                    <div className="font-medium text-pi-ink">{u.name || "—"}</div>
                    <div className="text-xs text-pi-ink-soft">{u.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs ${
                        u.role === "admin"
                          ? "bg-pi-ink text-pi-cream"
                          : "bg-pi-cream/60 text-pi-ink"
                      }`}
                    >
                      {u.role === "admin" ? "Admin" : "Usuario"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-pi-ink">{u.document_count ?? 0}</td>
                  <td className="px-4 py-3 text-pi-ink-soft">{formatDate(u.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "docs" && (
        <div className="overflow-hidden rounded-2xl border border-pi-gold-deep/15 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-pi-cream/40 text-left text-xs uppercase tracking-wide text-pi-gold-deep">
              <tr>
                <th className="px-4 py-3">Documento</th>
                <th className="px-4 py-3">Propietario</th>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-pi-gold-deep/10">
              {docs.map((d) => (
                <tr
                  key={d.id}
                  onClick={() => setSelected(d.id)}
                  className="cursor-pointer transition hover:bg-pi-cream/30"
                >
                  <td className="px-4 py-3 font-medium text-pi-ink">{d.filename}</td>
                  <td className="px-4 py-3 text-pi-ink-soft">{d.owner_email}</td>
                  <td className="px-4 py-3 text-pi-ink-soft">{kindLabel(d.kind)}</td>
                  <td className="px-4 py-3 text-pi-ink-soft">{formatDate(d.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selected !== null && (
        <DocumentDetailModal id={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}
