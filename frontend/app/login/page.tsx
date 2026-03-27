"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
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
                ? "entra a tu espacio calmado"
                : "crea una cuenta para adaptar la lectura",
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
            className="studio-panel w-full p-6 md:p-8"
        >
            <div className="grid gap-6 lg:grid-cols-[1.02fr_0.98fr]">
                <div className="rounded-[28px] bg-[rgba(255,255,255,0.62)] p-6 md:p-8">
                    <span className="eyebrow">Auth gateway</span>
                    <h1 className="display-title mt-5 text-5xl md:text-6xl">{headline}</h1>
                    <p className="muted-copy mt-5 max-w-xl text-base leading-8">
                        Entra para guardar tu perfil, cargar material y ver respuestas mas claras
                        desde una experiencia continua.
                    </p>

                    <div className="mt-8 grid gap-4 sm:grid-cols-2">
                        <button
                            onClick={() => setMode("login")}
                            className={mode === "login" ? "primary-button" : "secondary-button"}
                        >
                            Ya tengo cuenta
                        </button>
                        <button
                            onClick={() => setMode("register")}
                            className={mode === "register" ? "primary-button" : "secondary-button"}
                        >
                            Crear cuenta
                        </button>
                    </div>

                    <div className="mt-8 grid gap-3 sm:grid-cols-3">
                        <div className="tone-card">
                            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                                1
                            </p>
                            <p className="mt-2 text-sm leading-6 text-slate-700">
                                Entras o creas cuenta.
                            </p>
                        </div>
                        <div className="tone-card">
                            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                                2
                            </p>
                            <p className="mt-2 text-sm leading-6 text-slate-700">
                                Ajustas tu lectura.
                            </p>
                        </div>
                        <div className="tone-card">
                            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                                3
                            </p>
                            <p className="mt-2 text-sm leading-6 text-slate-700">
                                Subes y simplificas.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="rounded-[28px] bg-[linear-gradient(180deg,rgba(255,250,242,0.94),rgba(251,244,233,0.84))] p-6 md:p-8">
                    <div className="space-y-4">
                        {mode === "register" ? (
                            <div>
                                <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                            <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                            <label className="mb-2 block text-sm font-semibold text-slate-700">
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

                    <p className="mt-5 text-sm leading-6 text-slate-500">
                        {mode === "login"
                            ? "Entras directo a tu panel si tu perfil ya esta listo."
                            : "Despues del registro podras ajustar la experiencia antes de usar el chat."}
                    </p>

                    {error ? (
                        <div className="mt-4 rounded-2xl bg-[rgba(222,123,89,0.14)] p-4 text-sm text-[#96472f]">
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
