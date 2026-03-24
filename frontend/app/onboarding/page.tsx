"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import ReadingLevelInfo from "../../components/ReadingLevelInfo";
import { useUser } from "../../context/UserContext";
import { updateCurrentUser } from "../../lib/api";
import {
  createProfileFromDraft,
  readExperienceDraft,
} from "../../lib/profile";
import type {
  AccessibilityPreset,
  ConditionType,
  CognitivePriority,
  ReadingLevel,
  UserProfile,
} from "../../lib/types";

const priorityOptions: Array<{
  value: CognitivePriority;
  label: string;
  description: string;
}> = [
  {
    value: "focus",
    label: "Sostener foco",
    description: "Menos ruido visual y bloques mas estables.",
  },
  {
    value: "calm",
    label: "Reducir ansiedad",
    description: "Tono mas suave y menos sensacion de urgencia.",
  },
  {
    value: "contrast",
    label: "Mejor contraste",
    description: "Mas comodidad visual y lectura menos pesada.",
  },
  {
    value: "short_sentences",
    label: "Frases cortas",
    description: "Mas claridad por segmento y menos fatiga.",
  },
  {
    value: "step_by_step",
    label: "Paso a paso",
    description: "Secuencias concretas para tareas densas.",
  },
];

export default function Onboarding() {
  const router = useRouter();
  const { isAuthenticated, setProfile } = useUser();
  const initialDraft = readExperienceDraft();
  const initialProfile = createProfileFromDraft(initialDraft);
  const initialCondition: ConditionType =
    initialProfile.hasAdhd && initialProfile.hasDyslexia
      ? "combined"
      : initialProfile.hasDyslexia
        ? "dyslexia"
        : initialProfile.hasAdhd
          ? "adhd"
          : "manual";

  const [condition, setCondition] = useState<ConditionType>(initialCondition);
  const [readingLevel, setReadingLevel] = useState<ReadingLevel>(
    initialProfile.readingLevel,
  );
  const [tone, setTone] = useState<"calm_supportive" | "neutral_clear">(
    initialProfile.tone,
  );
  const [maxSentenceLength, setMaxSentenceLength] = useState(
    initialProfile.maxSentenceLength,
  );
  const [priorities, setPriorities] = useState<CognitivePriority[]>(
    initialProfile.priorities,
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasAdhd = condition === "adhd" || condition === "combined";
  const hasDyslexia = condition === "dyslexia" || condition === "combined";

  const preset: AccessibilityPreset =
    hasAdhd && hasDyslexia
      ? "combined"
      : hasDyslexia
        ? "dyslexia"
        : hasAdhd
          ? "adhd"
          : "custom";

  const recommendationCopy = useMemo(() => {
    if (hasAdhd && hasDyslexia) {
      return "Se prioriza estructura visual, contraste y frases cortas para sostener foco y reducir friccion lectora.";
    }

    if (hasAdhd) {
      return "Se prioriza continuidad visual, pasos concretos y menos densidad por bloque para sostener atencion.";
    }

    if (hasDyslexia) {
      return "Se prioriza claridad, contraste y menor fatiga lectora con frases mas faciles de procesar.";
    }

    return "Se crea un perfil equilibrado que luego puede afinarse segun tu forma de leer.";
  }, [hasAdhd, hasDyslexia]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

  const togglePriority = (value: CognitivePriority) => {
    setPriorities((current) =>
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value],
    );
  };

  const handleContinue = async () => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    const nextProfile: UserProfile = {
      hasAdhd,
      hasDyslexia,
      readingLevel,
      preset,
      maxSentenceLength,
      tone,
      priorities,
    };

    setSaving(true);
    setError(null);

    try {
      const savedProfile = await updateCurrentUser(nextProfile);
      setProfile(savedProfile);
    } catch {
      setError("No fue posible guardar tu perfil. Intenta nuevamente.");
      setSaving(false);
      return;
    }

    setSaving(false);
    router.push("/dashboard");
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="studio-panel w-full p-5 md:p-8"
    >
      <div className="panel-grid items-start xl:grid-cols-[1.05fr_0.95fr]">
        <motion.div
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.08, duration: 0.45 }}
          className="rounded-[28px] bg-[rgba(255,255,255,0.58)] p-6 md:p-8"
        >
          <span className="eyebrow">Cognitive setup</span>
          <h1 className="display-title mt-5 text-5xl md:text-7xl">
            personaliza
            <br />
            la lectura
            <br />
            segun tu ritmo
          </h1>
          <p className="muted-copy mt-5 max-w-xl text-base leading-7 md:text-lg">
            El sistema puede adaptar longitud de frases, tono, contraste y
            estructura visual. La idea es que la experiencia sea realista para
            TDAH, dislexia o combinacion de ambas.
          </p>

          <div className="mt-8 rounded-[24px] bg-white/70 p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
              Recomendacion actual
            </p>
            <p className="mt-3 text-base leading-7 text-slate-700">
              {recommendationCopy}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="status-pill">Preset: {preset}</span>
              <span className="status-pill">Frases de hasta {maxSentenceLength} palabras</span>
              <span className="status-pill">
                Tono {tone === "calm_supportive" ? "calmado" : "neutral"}
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.14, duration: 0.45 }}
          className="rounded-[28px] bg-[linear-gradient(180deg,rgba(255,255,255,0.92),rgba(255,247,235,0.86))] p-6 md:p-8"
        >
          <div className="flex items-center justify-between">
            <span className="eyebrow">Tu perfil</span>
            <span className="status-pill">{preset}</span>
          </div>

          <div className="mt-8 space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-600">
              Condicion o contexto principal
            </p>

            <div className="grid gap-3 sm:grid-cols-2">
              <button
                onClick={() => setCondition("adhd")}
                className={
                  condition === "adhd"
                    ? "tone-card border-[rgba(13,122,116,0.3)] bg-[rgba(213,235,225,0.44)] text-left"
                    : "tone-card text-left"
                }
              >
                <span className="block font-semibold text-slate-800">TDAH</span>
                <span className="mt-2 block text-sm leading-6 text-slate-600">
                  Menos ruido, bloques claros y continuidad visual.
                </span>
              </button>

              <button
                onClick={() => setCondition("dyslexia")}
                className={
                  condition === "dyslexia"
                    ? "tone-card border-[rgba(13,122,116,0.3)] bg-[rgba(213,235,225,0.44)] text-left"
                    : "tone-card text-left"
                }
              >
                <span className="block font-semibold text-slate-800">
                  Dislexia
                </span>
                <span className="mt-2 block text-sm leading-6 text-slate-600">
                  Lectura mas limpia, contraste y menos fatiga visual.
                </span>
              </button>

              <button
                onClick={() => setCondition("combined")}
                className={
                  condition === "combined"
                    ? "tone-card border-[rgba(13,122,116,0.3)] bg-[rgba(213,235,225,0.44)] text-left"
                    : "tone-card text-left"
                }
              >
                <span className="block font-semibold text-slate-800">
                  Ambas condiciones
                </span>
                <span className="mt-2 block text-sm leading-6 text-slate-600">
                  Combina estructura visual, contraste y frases mas cortas.
                </span>
              </button>

              <button
                onClick={() => setCondition("manual")}
                className={
                  condition === "manual"
                    ? "tone-card border-[rgba(13,122,116,0.3)] bg-[rgba(213,235,225,0.44)] text-left"
                    : "tone-card text-left"
                }
              >
                <span className="block font-semibold text-slate-800">
                  Personalizado
                </span>
                <span className="mt-2 block text-sm leading-6 text-slate-600">
                  Ajuste manual sin asociarlo a una condicion concreta.
                </span>
              </button>
            </div>
          </div>

          <div className="mt-6 space-y-5">
            <div>
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-slate-600">
                Nivel de lectura
              </label>
              <select
                className="app-select"
                value={readingLevel}
                onChange={(e) => setReadingLevel(e.target.value as ReadingLevel)}
              >
                <option>A1</option>
                <option>A2</option>
                <option>B1</option>
                <option>C1</option>
              </select>
              <div className="mt-3">
                <ReadingLevelInfo level={readingLevel} />
              </div>
            </div>

            <div>
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-slate-600">
                Tono de explicacion
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                <button
                  onClick={() => setTone("calm_supportive")}
                  className={
                    tone === "calm_supportive"
                      ? "primary-button justify-start"
                      : "secondary-button justify-start"
                  }
                >
                  Calmado y contenedor
                </button>
                <button
                  onClick={() => setTone("neutral_clear")}
                  className={
                    tone === "neutral_clear"
                      ? "primary-button justify-start"
                      : "secondary-button justify-start"
                  }
                >
                  Neutro y directo
                </button>
              </div>
            </div>

            <div>
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-slate-600">
                Longitud maxima de frase
              </label>
              <select
                className="app-select"
                value={maxSentenceLength}
                onChange={(e) => setMaxSentenceLength(Number(e.target.value))}
              >
                <option value={8}>8 palabras</option>
                <option value={10}>10 palabras</option>
                <option value={12}>12 palabras</option>
                <option value={15}>15 palabras</option>
              </select>
            </div>

            <div>
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-slate-600">
                Prioridades cognitivas
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                {priorityOptions.map((option) => {
                  const active = priorities.includes(option.value);

                  return (
                    <button
                      key={option.value}
                      onClick={() => togglePriority(option.value)}
                      className={
                        active
                          ? "tone-card border-[rgba(13,122,116,0.3)] bg-[rgba(213,235,225,0.44)] text-left"
                          : "tone-card text-left"
                      }
                    >
                      <span className="block font-semibold text-slate-800">
                        {option.label}
                      </span>
                      <span className="mt-2 block text-sm leading-6 text-slate-600">
                        {option.description}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={handleContinue}
              disabled={saving}
              className="primary-button flex-1"
            >
              {saving ? "Guardando..." : "Guardar perfil"}
            </button>
          </div>

          {error ? (
            <div className="mt-4 rounded-2xl bg-[rgba(222,123,89,0.14)] p-4 text-sm text-[#96472f]">
              {error}
            </div>
          ) : null}
        </motion.div>
      </div>
    </motion.section>
  );
}
