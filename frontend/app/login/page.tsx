"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import BrandMark from "../../components/BrandMark";
import { getCurrentUser, login, register } from "../../lib/api";
import { useUser } from "../../context/UserContext";

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, setAuthSession, setProfile } = useUser();

  const initialMode = searchParams.get("mode") === "register" ? "register" : "login";
  const [mode, setMode] = useState<"login" | "register">(initialMode);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const headline = useMemo(
    () =>
      mode === "login"
        ? "vuelve a tu espacio de lectura clara"
        : "crea una cuenta y personaliza el ambiente visual",
    [mode],
  );

  useEffect(() => {
    if (isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);

    try {
      const auth =
        mode === "login"
          ? await login({ email, password })
          : await register({ name, email, password });

      setAuthSession(auth.token, auth.user);

      const profile = await getCurrentUser();

      if (profile) {
        setProfile(profile);
        router.push("/dashboard");
      } else {
        router.push("/onboarding");
      }
    } catch {
      setError(
        mode === "login"
          ? "No fue posible iniciar sesion. Revisa tus datos."
          : "No fue posible crear la cuenta. Intenta nuevamente.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className="studio-panel hero-grid w-full p-6 md:p-8"
    >
      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="dark-studio-panel rounded-[30px] p-6 text-white md:p-8">
          <BrandMark showTagline />

          <span className="eyebrow mt-6">Acceso</span>
          <h1 className="display-title mt-5 text-5xl md:text-6xl">{headline}</h1>
          <p className="mt-5 max-w-xl text-base leading-8 text-white/78">
            La experiencia adapta paletas, tono y estructura visual desde
            preferencias de lectura. La seleccion se hace por comodidad, no por
            etiquetas visibles.
          </p>

          <div className="mt-6 flex flex-wrap gap-2">
            <span className="status-pill border-white/10 bg-white/10 text-white">
              Paletas por preferencia
            </span>
            <span className="status-pill border-white/10 bg-white/10 text-white">
              UI inspirada en la presentacion
            </span>
            <span className="status-pill border-white/10 bg-white/10 text-white">
              RAG listo para demo
            </span>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <button
              onClick={() => setMode("login")}
              className={
                mode === "login"
                  ? "primary-button shadow-[0_18px_30px_rgba(35,209,233,0.22)]"
                  : "secondary-button border-white/10 bg-white/10 text-white"
              }
            >
              Ya tengo cuenta
            </button>
            <button
              onClick={() => setMode("register")}
              className={
                mode === "register"
                  ? "primary-button shadow-[0_18px_30px_rgba(35,209,233,0.22)]"
                  : "secondary-button border-white/10 bg-white/10 text-white"
              }
            >
              Crear cuenta
            </button>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[24px] border border-white/10 bg-white/8 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/54">
                Paso 1
              </p>
              <p className="mt-2 text-sm leading-6 text-white/82">
                Entras o creas cuenta.
              </p>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/8 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/54">
                Paso 2
              </p>
              <p className="mt-2 text-sm leading-6 text-white/82">
                Eliges una paleta visual.
              </p>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/8 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/54">
                Paso 3
              </p>
              <p className="mt-2 text-sm leading-6 text-white/82">
                Subes, entiendes y conversas.
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-[30px] border border-white/10 bg-[rgba(10,18,27,0.72)] p-6 md:p-8">
          <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
            <span className="eyebrow">Cuenta</span>
            <span className="status-pill">
              {mode === "login" ? "Sesion existente" : "Registro nuevo"}
            </span>
          </div>

          <div className="space-y-4">
            {mode === "register" ? (
              <div>
                <label className="mb-2 block text-sm font-semibold text-white/82">
                  Nombre
                </label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="app-input"
                  placeholder="Tu nombre"
                />
              </div>
            ) : null}

            <div>
              <label className="mb-2 block text-sm font-semibold text-white/82">
                Email
              </label>
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="app-input"
                placeholder="nombre@correo.com"
                type="email"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-white/82">
                Contrasena
              </label>
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="app-input"
                placeholder="Minimo 8 caracteres"
                type="password"
              />
            </div>
          </div>

          <p className="mt-5 text-sm leading-6 text-white/64">
            {mode === "login"
              ? "Si tu perfil ya existe, entraras directo al panel principal."
              : "Despues del registro elegiras el ambiente visual que te resulte mas comodo."}
          </p>

          {error ? (
            <div className="mt-4 rounded-2xl border border-[rgba(255,125,108,0.22)] bg-[rgba(255,125,108,0.12)] p-4 text-sm text-[#ffd2cb]">
              {error}
            </div>
          ) : null}

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={handleSubmit}
              disabled={
                submitting ||
                email.trim().length === 0 ||
                password.trim().length === 0 ||
                (mode === "register" && name.trim().length === 0)
              }
              className="primary-button flex-1"
            >
              {submitting
                ? "Procesando..."
                : mode === "login"
                  ? "Entrar"
                  : "Crear cuenta"}
            </button>
          </div>

          <div className="mt-6 rounded-[22px] border border-white/10 bg-white/5 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent-cyan)]">
              Nota de experiencia
            </p>
            <p className="mt-2 text-sm leading-6 text-white/68">
              La interfaz usa paletas descriptivas como "Arena + cielo" o
              "Marfil + azul" para mantener una seleccion mas privada y
              responsable.
            </p>
          </div>
        </div>
      </div>
    </motion.section>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginPageContent />
    </Suspense>
  );
}
