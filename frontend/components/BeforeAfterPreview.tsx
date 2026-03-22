"use client";

import type { AccessibilityPreset } from "../lib/types";

type BeforeAfterPreviewProps = {
  preset: AccessibilityPreset;
  readingLevel: string;
  maxSentenceLength: number;
};

const beforeText =
  "El comite academico informa que el documento adjunto debe revisarse con caracter prioritario, considerando los requisitos, plazos, anexos y observaciones tecnicas distribuidas a lo largo de varias secciones.";

function getAfterText(
  preset: AccessibilityPreset,
  readingLevel: string,
  maxSentenceLength: number,
) {
  if (preset === "dyslexia") {
    return [
      "Revisa primero el documento adjunto.",
      "Tiene requisitos, fechas y anexos importantes.",
      `Usa frases cortas. Maximo sugerido: ${maxSentenceLength} palabras.`,
      `Nivel aplicado: ${readingLevel}.`,
    ];
  }

  if (preset === "adhd") {
    return [
      "Haz esto primero: abre el documento.",
      "Luego revisa requisitos y fechas clave.",
      "Despues mira anexos y observaciones tecnicas.",
      `Nivel aplicado: ${readingLevel}.`,
    ];
  }

  if (preset === "combined") {
    return [
      "Paso 1: abre el documento.",
      "Paso 2: identifica requisitos y fechas clave.",
      "Paso 3: revisa anexos por separado.",
      `Frases cortas y nivel ${readingLevel}.`,
    ];
  }

  return [
    "Abre el documento y revisa lo mas importante.",
    "Empieza por requisitos y fechas.",
    `Nivel aplicado: ${readingLevel}.`,
  ];
}

export default function BeforeAfterPreview({
  preset,
  readingLevel,
  maxSentenceLength,
}: BeforeAfterPreviewProps) {
  const afterLines = getAfterText(preset, readingLevel, maxSentenceLength);

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-[24px] border border-[rgba(23,49,59,0.1)] bg-[rgba(255,255,255,0.72)] p-5">
        <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
          Antes
        </p>
        <p className="mt-4 text-base leading-8 text-slate-700">{beforeText}</p>
      </div>

      <div className="rounded-[24px] border border-[rgba(13,122,116,0.18)] bg-[rgba(213,235,225,0.3)] p-5">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--teal-deep)]">
            Despues
          </p>
          <span className="status-pill">
            {preset} / {readingLevel}
          </span>
        </div>

        <div className="mt-4 space-y-3">
          {afterLines.map((line) => (
            <div
              key={line}
              className="rounded-2xl border border-white/60 bg-white/80 px-4 py-3 text-sm leading-7 text-slate-700"
            >
              {line}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
