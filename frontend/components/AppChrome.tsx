"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useUser } from "../context/UserContext";
import BrandMark from "./BrandMark";
import {
  createDraftFromPalette,
  getPaletteLabel,
  getPaletteSwatches,
  readExperienceDraft,
  subscribeExperienceDraft,
  writeExperienceDraft,
} from "../lib/profile";
import type { PalettePreference } from "../lib/types";

const navItems = [
  { href: "/dashboard", label: "Inicio" },
  { href: "/documents", label: "Documentos" },
  { href: "/chat", label: "Chat" },
];

const paletteOptions: PalettePreference[] = [
  "neutral",
  "calm",
  "contrast",
  "harmony",
];

export default function AppChrome({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { authUser, isAuthenticated, logout, profile } = useUser();
  const [draft, setDraft] = useState(() => readExperienceDraft());
  const [paletteMenuOpen, setPaletteMenuOpen] = useState(false);
  const paletteMenuRef = useRef<HTMLDivElement | null>(null);
  const palettePreference = draft.palettePreference;
  const paletteLabel = getPaletteLabel(palettePreference);
  const paletteSwatches = getPaletteSwatches(palettePreference);
  const isPublicRoute =
    pathname === "/" || pathname === "/login" || pathname.startsWith("/shared/");

  useEffect(() => {
    return subscribeExperienceDraft(() => {
      setDraft(readExperienceDraft());
    });
  }, []);

  useEffect(() => {
    if (!paletteMenuOpen) {
      return;
    }

    const handlePointerDown = (event: MouseEvent) => {
      if (!paletteMenuRef.current?.contains(event.target as Node)) {
        setPaletteMenuOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setPaletteMenuOpen(false);
      }
    };

    window.addEventListener("mousedown", handlePointerDown);
    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("mousedown", handlePointerDown);
      window.removeEventListener("keydown", handleEscape);
    };
  }, [paletteMenuOpen]);

  const paletteButton = (
    <div className="relative" ref={paletteMenuRef}>
      <button
        type="button"
        onClick={() => setPaletteMenuOpen((current) => !current)}
        className="secondary-button px-4 py-2 text-sm"
      >
        <span className="flex items-center gap-2">
          <span className="flex items-center">
            {paletteSwatches.map((color, index) => (
              <span
                key={`${color}-${index}`}
                className="-ml-1 inline-block h-3.5 w-3.5 rounded-full border border-white first:ml-0"
                style={{ backgroundColor: color }}
              />
            ))}
          </span>
          {paletteLabel}
        </span>
      </button>

      {paletteMenuOpen ? (
        <div className="absolute right-0 z-30 mt-3 w-[18rem] rounded-[22px] border border-white/10 bg-[rgba(17,22,30,0.94)] p-3 shadow-[0_24px_56px_rgba(0,0,0,0.32)] backdrop-blur-md">
          <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-[0.14em] text-white/60">
            Ambiente visual
          </p>
          <div className="space-y-2">
            {paletteOptions.map((option) => {
              const active = option === palettePreference;
              const swatches = getPaletteSwatches(option);

              return (
                <button
                  key={option}
                  type="button"
                  onClick={() => {
                    const seededDraft = createDraftFromPalette(option);
                    writeExperienceDraft({
                      ...draft,
                      ...seededDraft,
                      priorities:
                        draft.palettePreference === option
                          ? draft.priorities
                          : seededDraft.priorities,
                    });
                    setPaletteMenuOpen(false);
                  }}
                  className={
                    active
                      ? "flex w-full items-center justify-between rounded-2xl border border-[rgba(76,226,244,0.32)] bg-[rgba(76,226,244,0.12)] px-3 py-3 text-left shadow-[0_10px_28px_rgba(35,209,233,0.12)]"
                      : "flex w-full items-center justify-between rounded-2xl border border-white/8 bg-white/5 px-3 py-3 text-left hover:border-[rgba(76,226,244,0.18)]"
                  }
                >
                  <span className="block font-semibold text-white">
                    {getPaletteLabel(option)}
                  </span>
                  <span className="flex items-center gap-2">
                    {swatches.map((color, index) => (
                      <span
                        key={`${option}-${color}-${index}`}
                        className="inline-block h-3.5 w-3.5 rounded-full border border-white shadow-sm"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                    <span className="text-sm text-white/60">
                      {active ? "OK" : ""}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );

  if (isPublicRoute) {
    return (
      <div className="page-shell relative flex min-h-[calc(100vh-4rem)] flex-col gap-5">
        <header className="studio-panel sticky top-4 z-20 px-4 py-3 md:px-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <BrandMark compact />

            <div className="flex flex-wrap items-center gap-2">
              {paletteButton}
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
            <BrandMark compact />
            <span className="hidden rounded-full border border-white/8 bg-white/5 px-3 py-1.5 text-xs font-medium text-white/60 lg:inline-flex">
              {authUser ? `Sesion: ${authUser.name}` : "Workspace"}
            </span>
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
                      ? "rounded-full bg-[var(--accent-cyan)] px-4 py-2 text-sm font-semibold text-[#04131e] shadow-[0_10px_24px_rgba(35,209,233,0.24)]"
                      : "rounded-full border border-white/8 bg-white/6 px-4 py-2 text-sm font-semibold text-white/80 transition hover:bg-white/10"
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="flex flex-wrap items-center gap-2 text-sm">
            {paletteButton}
            <span className="status-pill">
              {profile ? `${paletteLabel} / ${profile.readingLevel}` : "Paleta pendiente"}
            </span>
            <Link href="/onboarding" className="secondary-button px-4 py-2 text-sm">
              Ajustar estilo
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
        <div className="rounded-2xl border border-white/8 bg-white/6 px-4 py-3 text-sm text-white/68 backdrop-blur-md">
          La experiencia ya une ambiente visual, documentos y conversacion en
          un flujo claro, accesible y listo para demostracion.
        </div>
        <div className="status-pill justify-center">
          Preferencia visual responsable
        </div>
      </footer>
    </div>
  );
}
