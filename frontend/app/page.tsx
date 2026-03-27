"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import BeforeAfterPreview from "../components/BeforeAfterPreview";
import PipelineTimeline from "../components/PipelineTimeline";
import { useUser } from "../context/UserContext";
import {
  applyIntensityToDraft,
  createDraftFromCondition,
  createProfileFromDraft,
  readExperienceDraft,
  writeExperienceDraft,
} from "../lib/profile";
import type {
  ConditionType,
  CognitivePriority,
  ExperienceDraft,
} from "../lib/types";

const conditionCards: Array<{
  condition: ConditionType;
  title: string;
  description: string;
}> = [
  {
    condition: "adhd",
    title: "Tengo TDAH",
    description: "Quiero menos ruido visual, pasos claros y foco sostenido.",
  },
  {
    condition: "dyslexia",
    title: "Tengo dislexia",
    description: "Necesito lectura mas limpia, contraste y menos fatiga.",
  },
  {
    condition: "combined",
    title: "Conviven ambas",
    description: "Quiero una interfaz estructurada, calmada y con apoyo visual.",
  },
  {
    condition: "manual",
    title: "Prefiero personalizar",
    description: "No quiero partir de una condicion, sino de mis necesidades.",
  },
  {
    condition: "unsure",
    title: "No estoy seguro",
    description: "Leer textos densos me cuesta y quiero probar adaptaciones.",
  },
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
  if (draft.condition === "combined") {
    return {
      shell: "bg-[#fbfcef] text-[#1f2b2a]",
      panel: "bg-white/80 border-[#c8d2b3]",
      accent: "bg-[#2c7e76] text-white",
    };
  }

  if (draft.condition === "dyslexia") {
    return {
      shell: "bg-[#fffdf4] text-[#1f1e1a] tracking-[0.03em]",
      panel: "bg-[#fffaf0] border-[#d8c888]",
      accent: "bg-[#2c7864] text-white",
    };
  }

  if (draft.condition === "adhd") {
    return {
      shell: "bg-[#f7fbfa] text-[#16323a]",
      panel: "bg-white border-[#b8d6d3]",
      accent: "bg-[#0a7d76] text-white",
    };
  }

  return {
    shell: "bg-[#fffaf2] text-[#17313b]",
    panel: "bg-white/80 border-[#d9d0c1]",
    accent: "bg-[#0d7a74] text-white",
  };
}

export default function Home() {
  const { isAuthenticated } = useUser();
  const [draft, setDraft] = useState<ExperienceDraft>(() => readExperienceDraft());

  useEffect(() => {
    writeExperienceDraft(draft);
  }, [draft]);

  const previewClasses = useMemo(() => getPreviewClasses(draft), [draft]);
  const previewProfile = useMemo(() => createProfileFromDraft(draft), [draft]);

  const handleConditionSelect = (condition: ConditionType) => {
    const seededDraft = createDraftFromCondition(condition);
    setDraft((currentDraft) => ({
      ...seededDraft,
      priorities:
        currentDraft.condition === condition
          ? currentDraft.priorities
          : seededDraft.priorities,
    }));
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
      className="studio-panel w-full overflow-hidden p-6 md:p-8"
    >
      <div className="grid gap-8 xl:grid-cols-[1fr_1fr]">
        <div className="space-y-6">
          <div className="rounded-[30px] bg-[rgba(255,255,255,0.62)] p-6 md:p-8">
            <span className="eyebrow">Experience setup</span>
            <h1 className="display-title mt-6 text-5xl md:text-7xl">
              adapta
              <br />
              la interfaz
              <br />
              a tu forma
              <br />
              de leer
            </h1>
            <p className="muted-copy mt-6 max-w-2xl text-base leading-8 md:text-lg">
              Elige una condicion o una necesidad concreta y mira como cambia
              la experiencia en tiempo real antes de crear cuenta.
            </p>

            <div className="mt-6 flex flex-wrap gap-2">
              <span className="status-pill">Cambio visual inmediato</span>
              <span className="status-pill">Lectura adaptada</span>
              <span className="status-pill">Demo guiada</span>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {conditionCards.map((card) => {
              const active = draft.condition === card.condition;

              return (
                <button
                  key={card.condition}
                  onClick={() => handleConditionSelect(card.condition)}
                  className={
                    active
                      ? "tone-card border-[rgba(13,122,116,0.28)] bg-[rgba(213,235,225,0.44)] text-left"
                      : "tone-card text-left"
                  }
                >
                  <span className="block text-lg font-semibold text-slate-800">
                    {card.title}
                  </span>
                  <span className="mt-3 block text-sm leading-7 text-slate-600">
                    {card.description}
                  </span>
                </button>
              );
            })}
          </div>

          <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="rounded-[28px] bg-[rgba(255,250,242,0.76)] p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
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
                          ? "tone-card border-[rgba(13,122,116,0.28)] bg-[rgba(213,235,225,0.44)] text-left"
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

            <div className="rounded-[28px] bg-[rgba(255,255,255,0.62)] p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
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
                          ? "tone-card border-[rgba(13,122,116,0.28)] bg-[rgba(213,235,225,0.44)] text-left"
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

          <div className="flex flex-col gap-3 sm:flex-row">
            <Link
              href={isAuthenticated ? "/onboarding" : "/login?mode=register"}
              className="primary-button"
            >
              {isAuthenticated
                ? "Continuar con esta configuracion"
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
          <div className={`rounded-[30px] border p-5 md:p-6 ${previewClasses.shell} ${previewClasses.panel}`}>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <span className="eyebrow">Vista previa viva</span>
              <div className="flex flex-wrap gap-2">
                <span className="status-pill">
                  {previewProfile.preset} / {previewProfile.readingLevel}
                </span>
                <span className="status-pill">
                  frases hasta {previewProfile.maxSentenceLength}
                </span>
              </div>
            </div>
            <p className="mt-5 max-w-2xl text-sm leading-7 opacity-80">
              Condicion base: {draft.condition}. Tono{" "}
              {previewProfile.tone === "calm_supportive" ? "calmado" : "neutro"}.
              Prioridades: {draft.priorities.join(", ") || "ninguna"}.
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

          <div className="studio-panel p-5 md:p-6">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
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
            <div className="studio-panel p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
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

            <div className="studio-panel p-5">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                Flujo de valor
              </p>
              <div className="mt-4">
                <PipelineTimeline
                  steps={[
                    {
                      title: "Perfil detectado",
                      description:
                        "La experiencia toma tu condicion y prioridades cognitivas.",
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
              <div className="mt-4 text-sm leading-7 text-slate-600">
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
