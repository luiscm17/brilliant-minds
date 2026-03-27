"use client";

import type { AccessibilityPreset } from "../lib/types";

type BeforeAfterPreviewProps = {
    preset: AccessibilityPreset;
    readingLevel: string;
    maxSentenceLength: number;
};

const beforeText =
    "El comite academico informa que el documento adjunto debe revisarse con caracter prioritario, considerando requisitos, plazos, anexos y observaciones tecnicas distribuidas a lo largo de varias secciones.";

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
            <div className="rounded-[24px] border border-[rgba(23,49,59,0.1)] bg-[rgba(255,255,255,0.72)] p-5">
                <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                        Antes
                    </p>
                    <span className="status-pill">Texto original</span>
                </div>
                <p className="mt-4 text-base leading-8 text-slate-700">{beforeText}</p>
            </div>

            <div className="rounded-[24px] border border-[rgba(13,122,116,0.18)] bg-[rgba(213,235,225,0.3)] p-5">
                <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--teal-deep)]">
                        Despues
                    </p>
                    <span className="status-pill">
                        {preset} · {readingLevel}
                    </span>
                </div>

                <div className="mt-4 space-y-3">
                    {afterBlocks.map((block) => (
                        <div
                            key={`${block.title}-${block.highlight}`}
                            className="rounded-2xl border border-white/60 bg-white/80 px-4 py-3"
                        >
                            <div className="flex items-center justify-between gap-3">
                                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--teal-deep)]">
                                    {block.title}
                                </p>
                                <span className="inline-flex rounded-full bg-[rgba(13,122,116,0.12)] px-3 py-1 text-xs font-semibold text-[var(--teal-deep)]">
                                    {block.highlight}
                                </span>
                            </div>
                            <p className="mt-3 text-sm leading-7 text-slate-700">{block.line}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
