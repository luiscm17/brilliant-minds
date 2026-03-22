"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useUser } from "../context/UserContext";

const navItems = [
  { href: "/dashboard", label: "Inicio" },
  { href: "/documents", label: "Documentos" },
  { href: "/chat", label: "Chat" },
];

const publicRoutes = new Set(["/", "/login"]);

export default function AppChrome({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { authUser, isAuthenticated, logout, profile } = useUser();
  const isPublicRoute = publicRoutes.has(pathname);

  if (isPublicRoute) {
    return (
      <div className="page-shell relative flex min-h-[calc(100vh-4rem)] flex-col gap-5">
        <header className="studio-panel sticky top-4 z-20 px-4 py-3 md:px-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,var(--gold)_0%,var(--coral)_100%)] text-lg font-bold text-white shadow-[0_12px_24px_rgba(222,123,89,0.24)]">
                DS
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--teal-deep)]">
                  DocSimplify
                </p>
                <p className="text-sm text-slate-600">
                  Cognitive accessibility for dense documents
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isAuthenticated ? (
                <Link href="/dashboard" className="primary-button px-5 py-2.5 text-sm">
                  Ir al espacio personal
                </Link>
              ) : (
                <>
                  <Link href="/login" className="secondary-button px-4 py-2 text-sm">
                    Entrar
                  </Link>
                  <Link href="/login?mode=register" className="primary-button px-5 py-2.5 text-sm">
                    Crear cuenta
                  </Link>
                </>
              )}
            </div>
          </div>
        </header>

        <main className="flex-1">{children}</main>
      </div>
    );
  }

  return (
    <div className="page-shell relative flex min-h-[calc(100vh-4rem)] flex-col gap-5">
      <header className="studio-panel sticky top-4 z-20 px-4 py-3 md:px-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,var(--gold)_0%,var(--coral)_100%)] text-lg font-bold text-white shadow-[0_12px_24px_rgba(222,123,89,0.24)]">
              DS
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--teal-deep)]">
                DocSimplify
              </p>
              <p className="text-sm text-slate-600">
                {authUser ? `Sesion: ${authUser.name}` : "Workspace"}
              </p>
            </div>
          </div>

          <nav className="flex flex-wrap gap-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    isActive
                      ? "rounded-full bg-[var(--ink)] px-4 py-2 text-sm font-semibold text-white"
                      : "rounded-full border border-[rgba(23,49,59,0.1)] bg-white/60 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-white"
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2 text-sm">
            <span className="status-pill">
              {profile ? `${profile.preset} / ${profile.readingLevel}` : "Perfil pendiente"}
            </span>
            <Link href="/onboarding" className="secondary-button px-4 py-2 text-sm">
              Ajustar perfil
            </Link>
            <button
              onClick={() => {
                logout();
                router.push("/login");
              }}
              className="secondary-button px-4 py-2 text-sm"
            >
              Salir
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1">{children}</main>

      <footer className="grid gap-3 pb-2 md:grid-cols-[1fr_auto] md:items-center">
        <div className="rounded-2xl border border-[rgba(23,49,59,0.08)] bg-white/55 px-4 py-3 text-sm text-slate-600 backdrop-blur-md">
          La experiencia ya separa autenticacion, perfil cognitivo, documentos y
          conversacion para quedar conectable al backend del MVP.
        </div>
        <div className="status-pill justify-center">
          Challenge: accesibilidad cognitiva
        </div>
      </footer>
    </div>
  );
}
