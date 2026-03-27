"use client";

import { useState } from "react";
import {
  getChatComprehension,
  getConceptMap,
  shareChatResult,
} from "../lib/api";
import type {
  ChatResponse,
  ComprehensionQuestion,
  ConceptMap,
} from "../lib/types";

type ChatResultCardProps = {
  chatId: string | null;
  response: ChatResponse;
};

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
    <>
      <p className="leading-7 text-slate-800">
        {response.simplifiedText || "Generando respuesta..."}
      </p>
      <p className="mt-3 border-t border-slate-200 pt-3 text-sm leading-6 text-slate-500">
        {response.explanation}
      </p>

      {response.emojiSummary ? (
        <div className="mt-3 text-2xl tracking-[0.2em]">{response.emojiSummary}</div>
      ) : null}

      <div className="mt-3 flex flex-wrap gap-2">
        {response.readingLevelUsed ? (
          <span className="status-pill">Nivel {response.readingLevelUsed}</span>
        ) : null}
        {response.presetUsed ? (
          <span className="status-pill">Preset {response.presetUsed}</span>
        ) : null}
        <span className="status-pill">Tono {response.tone}</span>
      </div>

      {response.wcagReport ? (
        <div className="mt-3 rounded-2xl bg-[rgba(13,122,116,0.08)] p-3 text-sm text-[var(--teal-deep)]">
          {response.wcagReport}
        </div>
      ) : null}

      {response.glossary && response.glossary.length > 0 ? (
        <details className="mt-3 rounded-2xl bg-white/70 p-3">
          <summary className="cursor-pointer text-sm font-semibold text-slate-700">
            Glosario
          </summary>
          <div className="mt-3 space-y-2 text-sm leading-6 text-slate-600">
            {response.glossary.map((entry) => (
              <div key={`${entry.word}-${entry.definition}`}>
                <span className="font-semibold text-slate-800">{entry.word}:</span>{" "}
                {entry.definition}
              </div>
            ))}
          </div>
        </details>
      ) : null}

      {response.searchesPerformed && response.searchesPerformed.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {response.searchesPerformed.map((query) => (
            <span key={query} className="status-pill">
              busqueda: {query}
            </span>
          ))}
        </div>
      ) : null}

      {chatId ? (
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            onClick={() => void handleQuiz()}
            disabled={loadingQuiz}
            className="secondary-button px-4 py-2 text-sm"
          >
            {loadingQuiz ? "Cargando quiz..." : "Quiz"}
          </button>
          <button
            onClick={() => void handleConceptMap()}
            disabled={loadingMap}
            className="secondary-button px-4 py-2 text-sm"
          >
            {loadingMap ? "Cargando mapa..." : "Mapa conceptual"}
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
        <div className="mt-3 rounded-2xl bg-[rgba(13,122,116,0.08)] p-3 text-sm text-[var(--teal-deep)]">
          <div className="break-all">{shareUrl}</div>
        </div>
      ) : null}

      {questions && questions.length > 0 ? (
        <div className="mt-3 rounded-2xl bg-white/70 p-3 text-sm">
          <p className="font-semibold text-slate-800">Comprension</p>
          <div className="mt-3 space-y-3 text-slate-600">
            {questions.map((question) => (
              <div key={question.question}>
                <p className="font-medium text-slate-800">{question.question}</p>
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
        <div className="mt-3 rounded-2xl bg-white/70 p-3 text-sm text-slate-600">
          <p className="font-semibold text-slate-800">Mapa conceptual</p>
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {conceptMap.nodes.map((node) => (
              <div key={node.id} className="rounded-xl border border-slate-200 bg-white p-3">
                {node.label}
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </>
  );
}
