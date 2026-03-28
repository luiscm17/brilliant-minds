"use client";

import type { AccessibilityPreset } from "../lib/types";

type BeforeAfterPreviewProps = {
  preset: AccessibilityPreset;
  readingLevel: string;
  maxSentenceLength: number;
};

const beforeText =
  "El comite academico informa que el documento adjunto debe revisarse con caracter prioritario, considerando requisitos, plazos, anexos y observaciones tecnicas distribuidas a lo largo de varias secciones.";

function getModeLabel(preset: AccessibilityPreset) {
  if (preset === "dyslexia") return "Marfil + azul";
  if (preset === "adhd") return "Arena + cielo";
  if (preset === "combined") return "Salvia + niebla";
  return "Base neutra";
}

function getAfterBlocks(
  preset: AccessibilityPreset,
  readingLevel: string,
  maxSentenceLength: number,
) {
  const levelBadge = `Nivel ${readingLevel}`;
  const sentenceBadge = `Frases hasta ${maxSentenceLength} palabras`;

  if (preset === "dyslexia") {
    return [
      {
        title: "Cambio 1",
        line: "Revisa primero el documento adjunto.",
        highlight: "frase corta",
      },
      {
        title: "Cambio 2",
        line: "Despues mira requisitos, fechas y anexos.",
        highlight: "orden claro",
      },
      {
        title: "Cambio 3",
        line: `${levelBadge}. ${sentenceBadge}.`,
        highlight: "menos carga lectora",
      },
    ];
  }

  if (preset === "adhd") {
    return [
      {
        title: "Paso 1",
        line: "Abre el documento y busca las fechas clave.",
        highlight: "inicio accionable",
      },
      {
        title: "Paso 2",
        line: "Luego revisa requisitos y anexos por separado.",
        highlight: "paso a paso",
      },
      {
        title: "Paso 3",
        line: `${levelBadge}. ${sentenceBadge}.`,
        highlight: "foco sostenido",
      },
    ];
  }

  if (preset === "combined") {
    return [
      {
        title: "Paso 1",
        line: "Abre el documento y ubica lo urgente primero.",
        highlight: "estructura + foco",
      },
      {
        title: "Paso 2",
        line: "Revisa requisitos, fechas y anexos en bloques separados.",
        highlight: "bloques cortos",
      },
      {
        title: "Paso 3",
        line: `${levelBadge}. ${sentenceBadge}.`,
        highlight: "contraste y claridad",
      },
    ];
  }

  return [
    {
      title: "Cambio 1",
      line: "Abre el documento y revisa primero lo importante.",
      highlight: "claridad general",
    },
    {
      title: "Cambio 2",
      line: `${levelBadge}. ${sentenceBadge}.`,
      highlight: "lenguaje mas simple",
    },
  ];
}

export default function BeforeAfterPreview({
  preset,
  readingLevel,
  maxSentenceLength,
}: BeforeAfterPreviewProps) {
  const afterBlocks = getAfterBlocks(preset, readingLevel, maxSentenceLength);

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-[24px] border border-white/10 bg-white/6 p-5">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/54">
            Antes
          </p>
          <span className="status-pill">Texto original</span>
        </div>
        <p className="mt-4 text-base leading-8 text-white/72">{beforeText}</p>
      </div>

      <div className="rounded-[24px] border border-[rgba(76,226,244,0.24)] bg-[rgba(76,226,244,0.12)] p-5">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--accent-cyan)]">
            Despues
          </p>
          <span className="status-pill">
            {getModeLabel(preset)} · {readingLevel}
          </span>
        </div>

        <div className="mt-4 space-y-3">
          {afterBlocks.map((block) => (
            <div
              key={`${block.title}-${block.highlight}`}
              className="rounded-2xl border border-white/10 bg-white/8 px-4 py-3"
            >
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent-cyan)]">
                  {block.title}
                </p>
                <span className="inline-flex rounded-full bg-[rgba(76,226,244,0.12)] px-3 py-1 text-xs font-semibold text-[var(--accent-cyan)]">
                  {block.highlight}
                </span>
              </div>
              <p className="mt-3 text-sm leading-7 text-white/72">
                {block.line}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
