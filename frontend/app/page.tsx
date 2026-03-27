"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import BeforeAfterPreview from "../components/BeforeAfterPreview";
import BrandMark from "../components/BrandMark";
import PipelineTimeline from "../components/PipelineTimeline";
import { useUser } from "../context/UserContext";
import {
  applyIntensityToDraft,
  createDraftFromPalette,
  createProfileFromDraft,
  getPaletteColorLine,
  getPaletteDescription,
  getPaletteLabel,
  getPaletteSwatches,
  readExperienceDraft,
  writeExperienceDraft,
} from "../lib/profile";
import type {
  CognitivePriority,
  ExperienceDraft,
  PalettePreference,
} from "../lib/types";

const paletteCards: Array<{
  palette: PalettePreference;
}> = [
  { palette: "calm" },
  { palette: "contrast" },
  { palette: "harmony" },
  { palette: "neutral" },
];

const supportOptions: Array<{
  value: CognitivePriority;
  label: string;
  description: string;
}> = [
  {
    value: "focus",
    label: "Menos distracciones",
    description: "Mas foco visual y menos competencia entre elementos.",
  },
  {
    value: "calm",
    label: "Tono mas calmado",
    description: "Reduce palabras de urgencia y baja la ansiedad.",
  },
  {
    value: "contrast",
    label: "Mejor contraste",
    description: "Hace el contenido mas estable visualmente.",
  },
  {
    value: "short_sentences",
    label: "Frases mas cortas",
    description: "Menos carga por bloque y lectura mas facil.",
  },
  {
    value: "step_by_step",
    label: "Explicacion paso a paso",
    description: "Convierte tareas densas en una secuencia clara.",
  },
];

const intensityOptions: Array<{
  value: ExperienceDraft["intensity"];
  label: string;
  description: string;
}> = [
  {
    value: "light",
    label: "Ligera",
    description: "Cambia lo justo, manteniendo una lectura relativamente normal.",
  },
  {
    value: "balanced",
    label: "Balanceada",
    description: "Equilibrio entre claridad, calma y estructura.",
  },
  {
    value: "strong",
    label: "Fuerte",
    description: "Maximiza contraste, frases cortas y apoyo visual.",
  },
];

function getPreviewClasses(draft: ExperienceDraft) {
  if (draft.palettePreference === "harmony") {
    return {
      shell: "bg-[#f5f8f1] text-[#1c1c1c]",
      panel: "bg-white/85 border-[#bfd7ea]",
    };
  }

  if (draft.palettePreference === "contrast") {
    return {
      shell: "bg-[#ffffff] text-[#000000] tracking-[0.03em]",
      panel: "bg-white border-[#004488]",
    };
  }

  if (draft.palettePreference === "calm") {
    return {
      shell: "bg-[#faf4e7] text-[#1c1c1c]",
      panel: "bg-white border-[#a7c7e7]",
    };
  }

  return {
    shell: "bg-[#fbf7ef] text-[#1c1c1c]",
    panel: "bg-white/80 border-[#dfe8cf]",
  };
}

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

export default function Home() {
  const { isAuthenticated } = useUser();
  const [draft, setDraft] = useState<ExperienceDraft>(() => readExperienceDraft());
  const [hoveredPalette, setHoveredPalette] = useState<PalettePreference | null>(null);
  const [flashPalette, setFlashPalette] = useState<PalettePreference | null>(null);

  useEffect(() => {
    writeExperienceDraft(draft);
  }, [draft]);

  useEffect(() => {
    if (!flashPalette) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setFlashPalette(null);
    }, 1200);

    return () => window.clearTimeout(timeoutId);
  }, [flashPalette]);

  const effectivePalette = hoveredPalette ?? draft.palettePreference;
  const previewDraft = useMemo(
    () =>
      hoveredPalette
        ? {
            ...draft,
            ...createDraftFromPalette(hoveredPalette),
            priorities: draft.priorities,
            intensity: draft.intensity,
          }
        : draft,
    [draft, hoveredPalette],
  );
  const previewClasses = useMemo(() => getPreviewClasses(previewDraft), [previewDraft]);
  const previewProfile = useMemo(() => createProfileFromDraft(previewDraft), [previewDraft]);

  const handlePaletteSelect = (palette: PalettePreference) => {
    const seededDraft = createDraftFromPalette(palette);
    setDraft((currentDraft) => ({
      ...seededDraft,
      priorities:
        currentDraft.palettePreference === palette
          ? currentDraft.priorities
          : seededDraft.priorities,
    }));
    setFlashPalette(palette);
  };

  const toggleSupport = (value: CognitivePriority) => {
    setDraft((currentDraft) => {
      const priorities = currentDraft.priorities.includes(value)
        ? currentDraft.priorities.filter((item) => item !== value)
        : [...currentDraft.priorities, value];

      return {
        ...currentDraft,
        priorities,
      };
    });
  };

  const setIntensity = (value: ExperienceDraft["intensity"]) => {
    setDraft((currentDraft) => applyIntensityToDraft(currentDraft, value));
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className="studio-panel hero-grid w-full overflow-hidden p-6 md:p-8"
    >
      <div className="grid gap-8 xl:grid-cols-[1fr_1fr]">
        <div className="space-y-6">
          <div className="dark-studio-panel rounded-[30px] p-6 text-white md:p-8">
            <BrandMark showTagline />
            <span className="eyebrow mt-6">Visual setup</span>
            <h1 className="display-title mt-6 text-5xl md:text-7xl">
              elige
              <br />
              tu paleta
              <br />
              favorita
              <br />
              para leer
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-8 text-white/80 md:text-lg">
              Antes de entrar a toda la interfaz, dinos que ambiente visual te
              hace sentir mas comodo. Desde ahi adaptamos colores, contraste y
              tipografia sin exponer etiquetas sensibles en la interfaz.
            </p>

            <div className="mt-6 flex flex-wrap gap-2">
              <span className="status-pill border-white/10 bg-white/10 text-white">
                Cambio visual inmediato
              </span>
              <span className="status-pill border-white/10 bg-white/10 text-white">
                Temas accesibles
              </span>
              <span className="status-pill border-white/10 bg-white/10 text-white">
                Demo guiada
              </span>
            </div>

            <motion.div
              key={flashPalette ?? draft.palettePreference}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.28, ease: "easeOut" }}
              className={`mt-6 inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/10 px-4 py-3 text-sm text-white ${flashPalette ? "shadow-[0_10px_28px_rgba(255,255,255,0.08)]" : ""}`}
              aria-live="polite"
            >
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white/16 text-sm font-semibold">
                {flashPalette ? "OK" : "•"}
              </span>
              <span>Aplicado: {getPaletteLabel(draft.palettePreference)}</span>
            </motion.div>
          </div>

          <div id="palette-selector" className="grid gap-4 sm:grid-cols-2">
            {paletteCards.map((card) => {
              const active = draft.palettePreference === card.palette;
              const swatches = getPaletteSwatches(card.palette);
              const preview = getPaletteCardPreview(card.palette);

              return (
                <button
                  key={card.palette}
                  onClick={() => handlePaletteSelect(card.palette)}
                  onMouseEnter={() => setHoveredPalette(card.palette)}
                  onMouseLeave={() => setHoveredPalette(null)}
                  onFocus={() => setHoveredPalette(card.palette)}
                  onBlur={() => setHoveredPalette(null)}
                  className={
                    active
                      ? "tone-card border-[rgba(76,226,244,0.42)] bg-[rgba(76,226,244,0.12)] text-left shadow-[0_20px_36px_rgba(35,209,233,0.12)] ring-2 ring-[rgba(76,226,244,0.14)]"
                      : "tone-card text-left hover:border-[rgba(76,226,244,0.24)] hover:shadow-[0_16px_30px_rgba(35,209,233,0.08)]"
                  }
                >
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <span className="eyebrow !px-3 !py-2">
                      {active ? "Seleccionada" : "Vista previa"}
                    </span>
                    <span
                      className={
                        active
                          ? "inline-flex h-8 w-8 items-center justify-center rounded-full bg-[var(--accent-cyan)] text-sm font-bold text-[#04131e] shadow-[0_8px_20px_rgba(35,209,233,0.24)]"
                          : "inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/12 bg-white text-[var(--teal-deep)]"
                      }
                    >
                      {active ? "OK" : ""}
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
                        key={`${card.palette}-${color}-${index}`}
                        className="inline-block h-4 w-4 rounded-full border border-white/90 shadow-sm"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </span>
                  <span className="block text-lg font-semibold text-white">
                    {getPaletteLabel(card.palette)}
                  </span>
                  <span className="mt-3 block text-sm leading-7 text-white/72">
                    {getPaletteDescription(card.palette)}
                  </span>
                  <span className="mt-4 block text-xs font-semibold uppercase tracking-[0.12em] text-[var(--accent-cyan)]">
                    {getPaletteColorLine(card.palette)}
                  </span>
                </button>
              );
            })}
          </div>

          <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="studio-panel hero-grid p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
                Intensidad de adaptacion
              </p>
              <div className="mt-4 space-y-3">
                {intensityOptions.map((option) => {
                  const active = draft.intensity === option.value;

                  return (
                    <button
                      key={option.value}
                      onClick={() => setIntensity(option.value)}
                      className={
                        active
                          ? "tone-card border-[rgba(76,226,244,0.28)] bg-[rgba(76,226,244,0.12)] text-left"
                          : "tone-card text-left"
                      }
                    >
                      <span className="block font-semibold text-white">
                        {option.label}
                      </span>
                      <span className="mt-2 block text-sm leading-6 text-white/72">
                        {option.description}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="studio-panel hero-grid p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
                Que te ayuda mas
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {supportOptions.map((option) => {
                  const active = draft.priorities.includes(option.value);

                  return (
                    <button
                      key={option.value}
                      onClick={() => toggleSupport(option.value)}
                      className={
                        active
                          ? "tone-card border-[rgba(76,226,244,0.28)] bg-[rgba(76,226,244,0.12)] text-left"
                          : "tone-card text-left"
                      }
                    >
                      <span className="block font-semibold text-white">
                        {option.label}
                      </span>
                      <span className="mt-2 block text-sm leading-6 text-white/72">
                        {option.description}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Link
              href={isAuthenticated ? "/onboarding" : "/login?mode=register"}
              className="primary-button"
            >
              {isAuthenticated
                ? "Continuar con este estilo"
                : "Crear cuenta y continuar"}
            </Link>
            <Link href="/login" className="secondary-button">
              Ya tengo cuenta
            </Link>
            <Link
              href={isAuthenticated ? "/chat?demo=1" : "/login?mode=register"}
              className="ghost-button"
            >
              Ver demo guiada
            </Link>
          </div>
        </div>

        <div className="space-y-5">
          <div
            className={`hero-grid rounded-[30px] border p-5 md:p-6 ${previewClasses.shell} ${previewClasses.panel}`}
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span className="eyebrow">Vista previa viva</span>
              <div className="flex flex-wrap gap-2">
                <span className="status-pill">
                  {getPaletteLabel(effectivePalette)} / {previewProfile.readingLevel}
                </span>
                <span className="status-pill">
                  frases hasta {previewProfile.maxSentenceLength}
                </span>
              </div>
            </div>
            <p className="mt-5 max-w-2xl text-sm leading-7 opacity-80">
              Vista actual: {getPaletteLabel(effectivePalette)}. Tono{" "}
              {previewProfile.tone === "calm_supportive" ? "calmado" : "neutro"}.
              Prioridades: {previewDraft.priorities.join(", ") || "ninguna"}.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl bg-white/65 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-60">
                  Foco
                </p>
                <p className="mt-2 text-sm leading-6">
                  Menos ruido y jerarquia mas clara.
                </p>
              </div>
              <div className="rounded-2xl bg-white/65 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-60">
                  Lectura
                </p>
                <p className="mt-2 text-sm leading-6">
                  Frases cortas y ritmo mas facil de seguir.
                </p>
              </div>
              <div className="rounded-2xl bg-white/65 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-60">
                  Tono
                </p>
                <p className="mt-2 text-sm leading-6">
                  Salida mas calmada y directa.
                </p>
              </div>
            </div>
          </div>

          <div className="studio-panel hero-grid p-5 md:p-6">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
              Antes vs despues
            </p>
            <div className="mt-5">
              <BeforeAfterPreview
                preset={previewProfile.preset}
                readingLevel={previewProfile.readingLevel}
                maxSentenceLength={previewProfile.maxSentenceLength}
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-[0.92fr_1.08fr]">
            <div className="studio-panel hero-grid p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
                Vista chat
              </p>
              <div className="mt-4 space-y-3">
                <div className="message-bubble-user mr-0 ml-auto max-w-[17rem]">
                  Explicame este documento con menos carga cognitiva.
                </div>
                <div className="message-bubble-ai max-w-[18rem]">
                  Voy a resumirlo con lenguaje mas directo, estructura paso a
                  paso y tono mas tranquilo.
                </div>
              </div>
            </div>

            <div className="studio-panel hero-grid p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
                Flujo de valor
              </p>
              <div className="mt-4">
                <PipelineTimeline
                  steps={[
                    {
                      title: "Paleta elegida",
                      description:
                        "La experiencia toma tus preferencias visuales y prioridades cognitivas.",
                      state: "done",
                    },
                    {
                      title: "Texto simplificado",
                      description:
                        "El sistema reorganiza frases, tono y estructura.",
                      state: "active",
                    },
                    {
                      title: "Respuesta explicable",
                      description:
                        "El usuario recibe una salida clara con razon de cambios.",
                      state: "idle",
                    },
                  ]}
                />
              </div>
              <div className="mt-4 text-sm leading-7 text-white/72">
                Muestra primero este cambio visual y luego pasa a documentos o
                chat para que la demo entre mas rapido.
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
