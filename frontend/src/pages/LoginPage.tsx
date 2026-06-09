import { useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth";
import logoFull from "../assets/logo-full.png";
import logoPiNad from "../assets/logo-pinad.png";

const FEATURES = [
  ["Escanea", "Sube fotos, PDF, Word, Excel o presentaciones — o usa la cámara de tu teléfono."],
  ["Extrae", "Leemos el contenido y detectamos montos, fechas, correos y datos clave."],
  ["Decide", "Tu dashboard inteligente resume todo y te muestra lo importante."],
];

type Mode = "login" | "register" | "verify";

export function LoginPage() {
  const { login } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [busy, setBusy] = useState(false);

  const reset = (next: Mode) => {
    setMode(next);
    setError("");
    setInfo("");
    setCode("");
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setInfo("");
    setBusy(true);
    try {
      const { token, user } = await api.login(email.trim(), password);
      login(token, user);
    } catch (err) {
      const msg = (err as Error).message;
      setError(msg);
      // El backend devuelve 403 y reenvía un código cuando falta verificar.
      if (msg.toLowerCase().includes("verificar")) {
        setInfo("Te enviamos un código a tu correo. Ingrésalo abajo.");
        setMode("verify");
      }
    } finally {
      setBusy(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setInfo("");
    setBusy(true);
    try {
      const res = await api.register(email.trim(), password, name.trim());
      setInfo(res.message);
      setMode("verify");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { token, user } = await api.verify(email.trim(), code.trim());
      login(token, user);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setInfo("");
    setBusy(true);
    try {
      const res = await api.resend(email.trim());
      setInfo(res.message);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const inputClass =
    "w-full rounded-lg border border-pi-gold-deep/30 bg-white px-3 py-2.5 text-sm outline-none focus:border-pi-gold focus:ring-2 focus:ring-pi-gold/30";
  const primaryBtn =
    "w-full rounded-lg bg-pi-gold px-4 py-2.5 text-sm font-medium text-white transition hover:bg-pi-gold-deep disabled:opacity-60";

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-2">
      {/* Hero / brand */}
      <div className="relative flex flex-col justify-between bg-pi-ink p-8 text-pi-cream lg:p-14">
        <div className="inline-flex w-fit rounded-xl bg-white px-4 py-3 shadow-lg">
          <img src={logoFull} alt="(π)NAD" className="h-12 w-auto" />
        </div>
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
          100% gratuito · Verificación por correo · Datos cifrados por sesión
        </div>
      </div>

      {/* Auth card */}
      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <img src={logoPiNad} alt="(π)NAD" className="mb-6 h-10 w-auto lg:hidden" />

          {mode !== "verify" && (
            <div className="mb-6 inline-flex rounded-lg border border-pi-gold-deep/20 bg-pi-cream/40 p-1 text-sm">
              <button
                type="button"
                onClick={() => reset("login")}
                className={`rounded-md px-4 py-1.5 font-medium transition ${
                  mode === "login" ? "bg-pi-gold text-white" : "text-pi-ink-soft"
                }`}
              >
                Iniciar sesión
              </button>
              <button
                type="button"
                onClick={() => reset("register")}
                className={`rounded-md px-4 py-1.5 font-medium transition ${
                  mode === "register" ? "bg-pi-gold text-white" : "text-pi-ink-soft"
                }`}
              >
                Crear cuenta
              </button>
            </div>
          )}

          {mode === "login" && (
            <>
              <h2 className="font-display text-3xl text-pi-ink">Bienvenido de vuelta</h2>
              <p className="mt-1 text-sm text-pi-ink-soft">
                Ingresa con tu correo y contraseña.
              </p>
            </>
          )}
          {mode === "register" && (
            <>
              <h2 className="font-display text-3xl text-pi-ink">Crea tu cuenta</h2>
              <p className="mt-1 text-sm text-pi-ink-soft">
                Te enviaremos un código de verificación a tu correo.
              </p>
            </>
          )}
          {mode === "verify" && (
            <>
              <h2 className="font-display text-3xl text-pi-ink">Verifica tu correo</h2>
              <p className="mt-1 text-sm text-pi-ink-soft">
                Escribe el código de 6 dígitos que enviamos a{" "}
                <span className="font-medium text-pi-ink">{email}</span>.
              </p>
            </>
          )}

          {error && (
            <div className="mt-4 rounded-lg border border-pi-brown/30 bg-pi-brown/10 px-3 py-2 text-sm text-pi-brown">
              {error}
            </div>
          )}
          {info && (
            <div className="mt-4 rounded-lg border border-pi-gold-deep/30 bg-pi-cream/50 px-3 py-2 text-sm text-pi-ink-soft">
              {info}
            </div>
          )}

          {mode === "login" && (
            <form onSubmit={handleLogin} className="mt-6 space-y-3">
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tucorreo@gmail.com"
                className={inputClass}
              />
              <input
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Contraseña"
                className={inputClass}
              />
              <button type="submit" disabled={busy} className={primaryBtn}>
                {busy ? "Entrando…" : "Entrar"}
              </button>
            </form>
          )}

          {mode === "register" && (
            <form onSubmit={handleRegister} className="mt-6 space-y-3">
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Tu nombre (opcional)"
                className={inputClass}
              />
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tucorreo@gmail.com"
                className={inputClass}
              />
              <input
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Contraseña (mínimo 8 caracteres)"
                className={inputClass}
              />
              <button type="submit" disabled={busy} className={primaryBtn}>
                {busy ? "Creando…" : "Crear cuenta"}
              </button>
            </form>
          )}

          {mode === "verify" && (
            <form onSubmit={handleVerify} className="mt-6 space-y-3">
              <input
                type="text"
                inputMode="numeric"
                required
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="000000"
                maxLength={6}
                className={`${inputClass} text-center text-2xl tracking-[0.5em]`}
              />
              <button type="submit" disabled={busy} className={primaryBtn}>
                {busy ? "Verificando…" : "Verificar y entrar"}
              </button>
              <div className="flex items-center justify-between pt-1 text-sm">
                <button
                  type="button"
                  onClick={handleResend}
                  disabled={busy}
                  className="text-pi-gold-deep hover:underline disabled:opacity-60"
                >
                  Reenviar código
                </button>
                <button
                  type="button"
                  onClick={() => reset("login")}
                  className="text-pi-ink-soft hover:underline"
                >
                  Volver
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
