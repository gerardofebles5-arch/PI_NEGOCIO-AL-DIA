import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth";
import { Logo } from "../components/Logo";

function NavItem({ to, label, onClick }: { to: string; label: string; onClick?: () => void }) {
  return (
    <NavLink
      to={to}
      end
      onClick={onClick}
      className={({ isActive }) =>
        `rounded-lg px-4 py-2 text-sm font-medium transition ${
          isActive
            ? "bg-pi-gold text-white"
            : "text-pi-ink-soft hover:bg-pi-cream/60"
        }`
      }
    >
      {label}
    </NavLink>
  );
}

export function AppLayout() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const nav = (
    <>
      <NavItem to="/" label="Dashboard" onClick={() => setMenuOpen(false)} />
      <NavItem to="/documentos" label="Documentos" onClick={() => setMenuOpen(false)} />
      {user?.role === "admin" && (
        <NavItem to="/admin" label="Admin" onClick={() => setMenuOpen(false)} />
      )}
    </>
  );

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-pi-gold-deep/15 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Logo size={38} />

          <nav className="hidden items-center gap-1 md:flex">{nav}</nav>

          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <div className="text-sm font-medium text-pi-ink">{user?.name || user?.email}</div>
              <div className="text-xs text-pi-gold-deep">
                {user?.role === "admin" ? "Administrador" : "Usuario"}
              </div>
            </div>
            {user?.picture ? (
              <img
                src={user.picture}
                alt=""
                className="h-9 w-9 rounded-full border border-pi-gold-deep/30 object-cover"
              />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-pi-ink text-sm font-medium text-pi-cream">
                {(user?.name || user?.email || "?").charAt(0).toUpperCase()}
              </div>
            )}
            <button
              onClick={logout}
              className="hidden rounded-lg border border-pi-gold-deep/30 px-3 py-1.5 text-sm text-pi-ink-soft transition hover:bg-pi-cream/60 sm:block"
            >
              Salir
            </button>
            <button
              onClick={() => setMenuOpen((o) => !o)}
              className="rounded-lg border border-pi-gold-deep/30 p-2 md:hidden"
              aria-label="Menú"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="flex flex-col gap-1 border-t border-pi-gold-deep/15 px-4 py-3 md:hidden">
            {nav}
            <button
              onClick={() => {
                setMenuOpen(false);
                logout();
              }}
              className="rounded-lg px-4 py-2 text-left text-sm text-pi-brown"
            >
              Salir
            </button>
          </div>
        )}
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 sm:py-8">
        <Outlet />
      </main>
    </div>
  );
}
