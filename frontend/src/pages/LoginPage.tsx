import { useEffect, useState } from "react";
import { api, type AuthConfig } from "../api";
import { useAuth } from "../auth";
import { Logo } from "../components/Logo";
import { GoogleSignIn } from "../components/GoogleSignIn";

const FEATURES = [
  ["Escanea", "Sube fotos, PDF, Word, Excel o presentaciones — o usa la cámara de tu teléfono."],
  ["Extrae", "Leemos el contenido y detectamos montos, fechas, correos y datos clave."],
  ["Decide", "Tu dashboard inteligente resume todo y te muestra lo importante."],
];

export function LoginPage() {
  const { login } = useAuth();
  const [config, setConfig] = useState<AuthConfig | null>(null);
  const [error, setError] = useState("");
  const [devEmail, setDevEmail] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.authConfig().then(setConfig).catch(() => setConfig(null));
  }, []);

  const handleGoogle = async (credential: string) => {
    setError("");
    try {
      const { token, user } = await api.googleLogin(credential);
      login(token, user);
    } catch (e) {
      setError((e as Error).message);
    }
  };

  const handleDev = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { token, user } = await api.devLogin(devEmail.trim());
      login(token, user);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-2">
      {/* Hero / brand */}
      <div className="relative flex flex-col justify-between bg-pi-ink p-8 text-pi-cream lg:p-14">
        <Logo size={48} />
        <div className="py-12">
          <h1 className="font-display text-5xl leading-[0.95] text-pi-cream sm:text-6xl">
            Tu información,
            <br />
            <span className="text-pi-gold-light">organizada</span> en segundos.
          </h1>
          <p className="mt-6 max-w-md text-pi-cream/80">
            (π)NAD escanea tus documentos e imágenes, extrae los datos y los
            archiva de forma segura para que siempre los tengas a mano.
          </p>
          <ul className="mt-8 space-y-4">
            {FEATURES.map(([title, desc]) => (
              <li key={title} className="flex gap-3">
                <span className="mt-1 h-2.5 w-2.5 flex-none rounded-full bg-pi-gold-light" />
                <div>
                  <div className="font-display text-xl tracking-wide text-pi-cream">
                    {title}
                  </div>
                  <div className="text-sm text-pi-cream/70">{desc}</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="text-xs text-pi-cream/50">
          100% gratuito · Datos cifrados por sesión
        </div>
      </div>

      {/* Auth card */}
      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <h2 className="font-display text-3xl text-pi-ink">Inicia sesión</h2>
          <p className="mt-1 text-sm text-pi-ink-soft">
            Accede con tu cuenta de Google para empezar.
          </p>

          {error && (
            <div className="mt-4 rounded-lg border border-pi-brown/30 bg-pi-brown/10 px-3 py-2 text-sm text-pi-brown">
              {error}
            </div>
          )}

          <div className="mt-6 space-y-4">
            {config?.google_enabled && config.google_client_id ? (
              <GoogleSignIn
                clientId={config.google_client_id}
                onCredential={handleGoogle}
              />
            ) : (
              <div className="rounded-lg border border-pi-gold-deep/30 bg-pi-cream/40 px-4 py-3 text-sm text-pi-ink-soft">
                El acceso con Google se activará en cuanto se configure el
                <span className="font-medium"> Client ID</span>.
              </div>
            )}

            {config?.dev_login_enabled && (
              <form onSubmit={handleDev} className="space-y-3 border-t border-pi-gold-deep/20 pt-5">
                <div className="text-xs font-medium uppercase tracking-wider text-pi-gold-deep">
                  Acceso de prueba
                </div>
                <input
                  type="email"
                  required
                  value={devEmail}
                  onChange={(e) => setDevEmail(e.target.value)}
                  placeholder="tucorreo@gmail.com"
                  className="w-full rounded-lg border border-pi-gold-deep/30 bg-white px-3 py-2.5 text-sm outline-none focus:border-pi-gold focus:ring-2 focus:ring-pi-gold/30"
                />
                <button
                  type="submit"
                  disabled={busy}
                  className="w-full rounded-lg bg-pi-gold px-4 py-2.5 text-sm font-medium text-white transition hover:bg-pi-gold-deep disabled:opacity-60"
                >
                  {busy ? "Entrando…" : "Entrar"}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
