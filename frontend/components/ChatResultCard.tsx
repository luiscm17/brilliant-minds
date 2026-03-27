"use client";

import { useState } from "react";
import Image from "next/image";
import {
  getChatComprehension,
  getConceptMap,
  shareChatResult,
} from "../lib/api";
import { getPaletteLabel, readExperienceDraft } from "../lib/profile";
import type {
  ChatResponse,
  ComprehensionQuestion,
  ConceptMap,
} from "../lib/types";

type ChatResultCardProps = {
  chatId: string | null;
  response: ChatResponse;
};

function resolveVisualUrl(imageUrl?: string | null, path?: string | null) {
  const candidate = imageUrl || path;
  if (!candidate) {
    return null;
  }

  if (candidate.startsWith("http://") || candidate.startsWith("https://")) {
    return candidate;
  }

  if (!path || path.includes("/")) {
    return null;
  }

  try {
    const decoded = atob(path);
    if (decoded.startsWith("http://") || decoded.startsWith("https://")) {
      return decoded;
    }
  } catch {
    return null;
  }

  return null;
}

export default function ChatResultCard({
  chatId,
  response,
}: ChatResultCardProps) {
  const [questions, setQuestions] = useState<ComprehensionQuestion[] | null>(null);
  const [conceptMap, setConceptMap] = useState<ConceptMap | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [loadingQuiz, setLoadingQuiz] = useState(false);
  const [loadingMap, setLoadingMap] = useState(false);
  const [sharing, setSharing] = useState(false);
  const currentPaletteLabel = getPaletteLabel(readExperienceDraft().palettePreference);

  const handleQuiz = async () => {
    if (!chatId) return;
    setLoadingQuiz(true);
    try {
      const result = await getChatComprehension(chatId, response.simplifiedText);
      setQuestions(result.questions);
    } finally {
      setLoadingQuiz(false);
    }
  };

  const handleConceptMap = async () => {
    if (!chatId) return;
    setLoadingMap(true);
    try {
      setConceptMap(await getConceptMap(chatId, response.simplifiedText));
    } finally {
      setLoadingMap(false);
    }
  };

  const handleShare = async () => {
    if (!chatId) return;
    setSharing(true);
    try {
      const result = await shareChatResult(chatId, response);
      setShareUrl(result.shareUrl);
    } finally {
      setSharing(false);
    }
  };

  return (
    <div className="reading-stack">
      <p className="reading-text">{response.simplifiedText || "Generando respuesta..."}</p>
      <p className="reading-subtle border-t border-white/10 pt-3">
        {response.explanation}
      </p>

      {response.emojiSummary ? (
        <div className="text-2xl tracking-[0.2em]">{response.emojiSummary}</div>
      ) : null}

      <div className="flex flex-wrap gap-2">
        {response.readingLevelUsed ? (
          <span className="status-pill">Nivel {response.readingLevelUsed}</span>
        ) : null}
        {response.presetUsed ? (
          <span className="status-pill">
            Estilo {response.presetUsed === "custom" ? currentPaletteLabel : response.presetUsed}
          </span>
        ) : null}
        <span className="status-pill">Tono {response.tone}</span>
      </div>

      {response.wcagReport ? (
        <div className="rounded-2xl border border-[rgba(76,226,244,0.2)] bg-[rgba(76,226,244,0.08)] p-3 text-sm text-white/84">
          {response.wcagReport}
        </div>
      ) : null}

      {response.glossary && response.glossary.length > 0 ? (
        <details className="rounded-2xl border border-white/10 bg-white/8 p-4">
          <summary className="cursor-pointer text-sm font-semibold text-white">
            Glosario
          </summary>
          <div className="mt-3 space-y-2 text-sm leading-7 text-white/74">
            {response.glossary.map((entry) => (
              <div key={`${entry.word}-${entry.definition}`}>
                <span className="font-semibold text-white">{entry.word}:</span>{" "}
                {entry.definition}
              </div>
            ))}
          </div>
        </details>
      ) : null}

      {response.searchesPerformed && response.searchesPerformed.length > 0 ? (
        <div className="flex flex-wrap gap-2">
          {response.searchesPerformed.map((query) => (
            <span key={query} className="status-pill">
              consulta: {query}
            </span>
          ))}
        </div>
      ) : null}

      {response.visualReferences && response.visualReferences.length > 0 ? (
        <details className="rounded-2xl border border-white/10 bg-white/8 p-4">
          <summary className="cursor-pointer text-sm font-semibold text-white">
            Evidencia visual
          </summary>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {response.visualReferences.map((reference, index) => {
              const visualUrl = resolveVisualUrl(reference.imageUrl, reference.path);
              return (
                <div
                  key={`${reference.path ?? reference.title ?? "visual"}-${index}`}
                  className="rounded-2xl border border-white/10 bg-white/8 p-3 text-sm text-white/72"
                >
                  <p className="font-semibold text-white">
                    {reference.title || "Referencia del documento"}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="status-pill">{reference.kind}</span>
                    {reference.sourceKind ? (
                      <span className="status-pill">{reference.sourceKind}</span>
                    ) : null}
                    {reference.sectionKind ? (
                      <span className="status-pill">{reference.sectionKind}</span>
                    ) : null}
                    {reference.pageNumber ? (
                      <span className="status-pill">pagina {reference.pageNumber}</span>
                    ) : null}
                  </div>
                  {visualUrl ? (
                    <a
                      href={visualUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-3 block overflow-hidden rounded-2xl border border-white/10 bg-black/10"
                    >
                      <Image
                        src={visualUrl}
                        alt={reference.imageCaption || reference.title || "Evidencia visual"}
                        width={640}
                        height={320}
                        unoptimized
                        className="h-44 w-full object-cover"
                      />
                    </a>
                  ) : null}
                  {reference.imageCaption ? (
                    <p className="mt-2 leading-7 text-white/78">{reference.imageCaption}</p>
                  ) : null}
                  {reference.previewText ? (
                    <p className="mt-2 leading-7">{reference.previewText}</p>
                  ) : null}
                  {reference.path ? (
                    <p className="mt-2 break-all text-xs text-white/46">{reference.path}</p>
                  ) : null}
                </div>
              );
            })}
          </div>
        </details>
      ) : null}

      {chatId ? (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => void handleQuiz()}
            disabled={loadingQuiz}
            className="secondary-button px-4 py-2 text-sm"
          >
            {loadingQuiz ? "Preparando quiz..." : "Quiz"}
          </button>
          <button
            onClick={() => void handleConceptMap()}
            disabled={loadingMap}
            className="secondary-button px-4 py-2 text-sm"
          >
            {loadingMap ? "Preparando mapa..." : "Mapa conceptual"}
          </button>
          <button
            onClick={() => void handleShare()}
            disabled={sharing}
            className="ghost-button px-4 py-2 text-sm"
          >
            {sharing ? "Compartiendo..." : "Compartir"}
          </button>
        </div>
      ) : null}

      {shareUrl ? (
        <div className="rounded-2xl border border-[rgba(76,226,244,0.2)] bg-[rgba(76,226,244,0.08)] p-3 text-sm text-white/84">
          <div className="break-all">{shareUrl}</div>
        </div>
      ) : null}

      {questions && questions.length > 0 ? (
        <div className="rounded-2xl border border-white/10 bg-white/8 p-4 text-sm">
          <p className="font-semibold text-white">Comprension</p>
          <div className="mt-3 space-y-3 text-white/74">
            {questions.map((question) => (
              <div key={question.question}>
                <p className="font-medium text-white">{question.question}</p>
                <div className="mt-2 space-y-1">
                  {Object.entries(question.options).map(([key, value]) => (
                    <div key={key}>
                      {key}. {value}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {conceptMap && conceptMap.nodes.length > 0 ? (
        <div className="rounded-2xl border border-white/10 bg-white/8 p-4 text-sm text-white/74">
          <p className="font-semibold text-white">Mapa conceptual</p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {conceptMap.nodes.map((node) => (
              <div key={node.id} className="rounded-xl border border-white/10 bg-white/8 p-3">
                {node.label}
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
