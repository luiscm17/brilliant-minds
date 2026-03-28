"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import BrandMark from "../../components/BrandMark";
import ReadingLevelInfo from "../../components/ReadingLevelInfo";
import { useUser } from "../../context/UserContext";
import { updateCurrentUser } from "../../lib/api";
import {
  createDraftFromPalette,
  createProfileFromDraft,
  deriveConditionFromPalette,
  getPaletteColorLine,
  getPaletteDescription,
  getPaletteLabel,
  getPaletteSwatches,
  readExperienceDraft,
  writeExperienceDraft,
} from "../../lib/profile";
import type {
  CognitivePriority,
  PalettePreference,
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

const paletteOptions: PalettePreference[] = [
  "calm",
  "contrast",
  "harmony",
  "neutral",
];

function getPaletteCardPreview(palette: PalettePreference) {
  switch (palette) {
    case "calm":
      return {
        shell:
          "bg-[linear-gradient(135deg,#f5eedc_0%,#faf4e7_52%,#ffffff_100%)]",
        accent: "bg-[#a7c7e7]",
        soft: "bg-[#cfe1b9]",
        ink: "bg-[#587b9f]",
      };
    case "contrast":
      return {
        shell:
          "bg-[linear-gradient(135deg,#ffffff_0%,#f8fbff_48%,#eef5fb_100%)]",
        accent: "bg-[#004488]",
        soft: "bg-[#ee7733]",
        ink: "bg-[#111111]",
      };
    case "harmony":
      return {
        shell:
          "bg-[linear-gradient(135deg,#eaf0e3_0%,#f5f8f1_50%,#ffffff_100%)]",
        accent: "bg-[#bfd7ea]",
        soft: "bg-[#c1e1c1]",
        ink: "bg-[#5a7288]",
      };
    default:
      return {
        shell:
          "bg-[linear-gradient(135deg,#fbf7ef_0%,#f4efe4_52%,#ffffff_100%)]",
        accent: "bg-[#dfe8cf]",
        soft: "bg-[#ee7733]",
        ink: "bg-[#1c1c1c]",
      };
  }
}

export default function Onboarding() {
  const router = useRouter();
  const { isAuthenticated, setProfile } = useUser();
  const initialDraft = readExperienceDraft();
  const initialProfile = createProfileFromDraft(initialDraft);

  const [palettePreference, setPalettePreference] = useState<PalettePreference>(
    initialDraft.palettePreference,
  );
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
  const [hoveredPalette, setHoveredPalette] = useState<PalettePreference | null>(
    null,
  );
  const [flashPalette, setFlashPalette] = useState<PalettePreference | null>(null);

  const resolvedCondition = deriveConditionFromPalette(palettePreference);

  const recommendationCopy = useMemo(() => {
    if (palettePreference === "harmony") {
      return "Equilibra contraste, estructura visual y frases cortas para sostener un ritmo estable de lectura.";
    }

    if (palettePreference === "calm") {
      return "Suaviza la interfaz con tonos relajados, bloques estables y menos saturacion visual.";
    }

    if (palettePreference === "contrast") {
      return "Sube el contraste, refuerza la jerarquia visual y limpia la lectura para recorridos mas claros.";
    }

    return "Parte de una base flexible y luego afina tono, densidad y prioridades a tu ritmo.";
  }, [palettePreference]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    if (!flashPalette) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setFlashPalette(null);
    }, 1200);

    return () => window.clearTimeout(timeoutId);
  }, [flashPalette]);

  const togglePriority = (value: CognitivePriority) => {
    setPriorities((current) =>
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value],
    );
  };

  const applyPalettePreference = (nextPalette: PalettePreference) => {
    const seededDraft = createDraftFromPalette(nextPalette);
    setPalettePreference(nextPalette);
    setReadingLevel(seededDraft.readingLevel);
    setTone(seededDraft.tone);
    setMaxSentenceLength(seededDraft.maxSentenceLength);
    setPriorities(seededDraft.priorities);
    setFlashPalette(nextPalette);
  };

  const handleContinue = async () => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    const nextDraft = {
      ...initialDraft,
      palettePreference,
      condition: resolvedCondition,
      readingLevel,
      maxSentenceLength,
      tone,
      priorities,
    };
    writeExperienceDraft(nextDraft);

    const nextProfile: UserProfile = createProfileFromDraft(nextDraft);

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
      className="studio-panel hero-grid w-full p-5 md:p-8"
    >
      <div className="panel-grid items-start xl:grid-cols-[1.05fr_0.95fr]">
        <motion.div
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.08, duration: 0.45 }}
          className="space-y-5 xl:sticky xl:top-28"
        >
          <div className="dark-studio-panel rounded-[28px] p-6 text-white md:p-8">
            <BrandMark showTagline />
            <span className="eyebrow mt-6">Visual onboarding</span>
            <h1 className="display-title mt-5 text-5xl md:text-7xl">
              comienza
              <br />por el
              <br />ambiente
              <br />visual
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-white/80 md:text-lg">
              El sistema puede adaptar longitud de frases, tono, contraste y
              estructura visual. Todo parte de la paleta que te hace sentir mas
              comodo al leer.
            </p>

            <div className="mt-8 rounded-[24px] border border-white/10 bg-white/10 p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/56">
                Recomendacion actual
              </p>
              <p className="mt-3 text-base leading-7 text-white/82">
                {recommendationCopy}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="status-pill border-white/10 bg-white/10 text-white">
                  Paleta: {getPaletteLabel(palettePreference)}
                </span>
                <span className="status-pill border-white/10 bg-white/10 text-white">
                  Frases de hasta {maxSentenceLength} palabras
                </span>
                <span className="status-pill border-white/10 bg-white/10 text-white">
                  Tono {tone === "calm_supportive" ? "calmado" : "neutral"}
                </span>
              </div>

              <motion.div
                key={flashPalette ?? palettePreference}
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.28, ease: "easeOut" }}
                className={`mt-5 inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/10 px-4 py-3 text-sm text-white ${flashPalette ? "shadow-[0_10px_28px_rgba(255,255,255,0.08)]" : ""}`}
                aria-live="polite"
              >
                <span className="inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-white/16 px-2 text-[11px] font-semibold uppercase tracking-[0.12em]">
                  {flashPalette ? "OK" : "Ahora"}
                </span>
                <span>Aplicado: {getPaletteLabel(palettePreference)}</span>
              </motion.div>
            </div>
          </div>

          <div className="studio-panel hero-grid rounded-[28px] p-5 md:p-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-[24px] border border-white/8 bg-white/6 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/56">
                  Interfaz
                </p>
                <p className="mt-3 text-sm leading-6 text-white/72">
                  La paleta cambia fondo, tarjetas, botones y jerarquia visual
                  antes de entrar al panel.
                </p>
              </div>
              <div className="rounded-[24px] border border-white/8 bg-white/6 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/56">
                  Lectura
                </p>
                <p className="mt-3 text-sm leading-6 text-white/72">
                  Aqui tambien ajustas frases, tono y ayudas cognitivas sin
                  cambiar nada del backend.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.14, duration: 0.45 }}
          className="rounded-[28px] border border-white/10 bg-[rgba(10,18,27,0.72)] p-6 md:p-8"
        >
          <div className="flex items-center justify-between">
            <span className="eyebrow">Tu estilo</span>
            <span className="status-pill">{getPaletteLabel(palettePreference)}</span>
          </div>

          <div className="mt-8 space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/62">
              Que ambiente visual te ayuda mas
            </p>

            <div className="grid gap-3 sm:grid-cols-2">
              {paletteOptions.map((option) => {
                const active = palettePreference === option;
                const swatches = getPaletteSwatches(option);
                const preview = getPaletteCardPreview(option);

                return (
                  <button
                    key={option}
                    type="button"
                    onClick={() => applyPalettePreference(option)}
                    onMouseEnter={() => setHoveredPalette(option)}
                    onMouseLeave={() => setHoveredPalette(null)}
                    onFocus={() => setHoveredPalette(option)}
                    onBlur={() => setHoveredPalette(null)}
                    className={
                      active
                        ? "tone-card border-[rgba(76,226,244,0.42)] bg-[rgba(76,226,244,0.12)] text-left shadow-[0_18px_34px_rgba(35,209,233,0.12)] ring-2 ring-[rgba(76,226,244,0.14)]"
                        : "tone-card text-left hover:border-[rgba(76,226,244,0.24)] hover:shadow-[0_16px_30px_rgba(35,209,233,0.08)]"
                    }
                  >
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <span className="eyebrow !px-3 !py-2">
                        {active
                          ? "Seleccionada"
                          : hoveredPalette === option
                            ? "Preview"
                            : "Opcion"}
                      </span>
                      <span
                        className={
                          active
                            ? "inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-[var(--accent-cyan)] px-2 text-[11px] font-bold uppercase tracking-[0.12em] text-[#04131e] shadow-[0_8px_20px_rgba(35,209,233,0.24)]"
                            : "inline-flex h-8 min-w-8 items-center justify-center rounded-full border border-white/12 bg-white px-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--teal-deep)]"
                        }
                      >
                        {active ? "OK" : "Ver"}
                      </span>
                    </div>

                    <div
                      className={`mb-4 overflow-hidden rounded-[18px] border border-white/80 p-3 ${preview.shell}`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-2">
                          <div className={`h-2.5 w-16 rounded-full ${preview.ink} opacity-90`} />
                          <div className={`h-2.5 w-24 rounded-full ${preview.ink} opacity-55`} />
                          <div className={`h-2.5 w-20 rounded-full ${preview.ink} opacity-35`} />
                        </div>
                        <div className="space-y-2">
                          <div className={`h-8 w-8 rounded-2xl ${preview.accent} shadow-sm`} />
                          <div className={`h-5 w-12 rounded-full ${preview.soft} opacity-90`} />
                        </div>
                      </div>
                      <div className="mt-3 flex gap-2">
                        <div className={`h-10 flex-1 rounded-2xl ${preview.accent} opacity-90`} />
                        <div className={`h-10 w-16 rounded-2xl ${preview.soft}`} />
                      </div>
                    </div>

                    <span className="flex items-center gap-2">
                      {swatches.map((color, index) => (
                        <span
                          key={`${option}-${color}-${index}`}
                          className="inline-block h-4 w-4 rounded-full border border-white/90 shadow-sm"
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </span>
                    <span className="block font-semibold text-white">
                      {getPaletteLabel(option)}
                    </span>
                    <span className="mt-2 block text-sm leading-6 text-white/68">
                      {getPaletteDescription(option)}
                    </span>
                    <span className="mt-3 block text-xs font-semibold uppercase tracking-[0.12em] text-[var(--teal-deep)]">
                      {getPaletteColorLine(option)}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-6 space-y-5">
            <div>
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-white/62">
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
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-white/62">
                Tono de explicacion
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                <button
                  type="button"
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
                  type="button"
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
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-white/62">
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
              <label className="mb-3 block text-sm font-semibold uppercase tracking-[0.14em] text-white/62">
                Prioridades cognitivas
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                {priorityOptions.map((option) => {
                  const active = priorities.includes(option.value);

                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => togglePriority(option.value)}
                      className={
                        active
                          ? "tone-card border-[rgba(76,226,244,0.3)] bg-[rgba(76,226,244,0.12)] text-left"
                          : "tone-card text-left"
                      }
                    >
                      <span className="block font-semibold text-white">
                        {option.label}
                      </span>
                      <span className="mt-2 block text-sm leading-6 text-white/68">
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
              type="button"
              onClick={handleContinue}
              disabled={saving}
              className="primary-button flex-1"
            >
              {saving ? "Guardando..." : "Guardar estilo"}
            </button>
          </div>

          {error ? (
            <div className="mt-4 rounded-2xl border border-[rgba(255,125,108,0.22)] bg-[rgba(255,125,108,0.12)] p-4 text-sm text-[#ffd2cb]">
              {error}
            </div>
          ) : null}
        </motion.div>
      </div>
    </motion.section>
  );
}
