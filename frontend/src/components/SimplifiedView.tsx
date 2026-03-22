import { useState, useRef } from "react";
import { useAccessibilityStore } from "../store/accessibility";
import type { SimplifiedResponse } from "../api/endpoints";
import { chatsApi } from "../api/endpoints";
import WcagBadge from "./WcagBadge";
import ComprehensionQuiz from "./ComprehensionQuiz";
import ConceptMap from "./ConceptMap";

interface Props {
  result: SimplifiedResponse;
  chatId: string;
  onResimplify?: () => void;
  onExportPdf?: () => void;
}

export default function SimplifiedView({ result, chatId, onResimplify, onExportPdf }: Props) {
  const { beelineActive } = useAccessibilityStore();
  const [showComparison, setShowComparison] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [sharing, setSharing] = useState(false);
  const [guidedActive, setGuidedActive] = useState(false);
  const [activeWordIdx, setActiveWordIdx] = useState(-1);
  const uttRef = useRef<SpeechSynthesisUtterance | null>(null);

  const lines = result.simplified_text.split(/\r?\n/).filter((l) => l.trim());
  const beelineColors = ["#1d4ed8", "#b45309"];

  const speakLine = (text: string) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = "es-ES";
    utt.rate = 0.9;
    window.speechSynthesis.speak(utt);
  };

  const startGuidedReading = () => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(result.simplified_text);
    utt.lang = "es-ES";
    utt.rate = 0.85;
    utt.onboundary = (e) => {
      if (e.name === "word") {
        const spoken = result.simplified_text.slice(0, e.charIndex + e.charLength);
        const idx = spoken.trim().split(/\s+/).length - 1;
        setActiveWordIdx(idx);
      }
    };
    utt.onend = () => { setGuidedActive(false); setActiveWordIdx(-1); };
    utt.onerror = () => { setGuidedActive(false); setActiveWordIdx(-1); };
    uttRef.current = utt;
    setGuidedActive(true);
    window.speechSynthesis.speak(utt);
  };

  const stopGuidedReading = () => {
    window.speechSynthesis.cancel();
    setGuidedActive(false);
    setActiveWordIdx(-1);
  };

  const handleShare = async () => {
    setSharing(true);
    try {
      const res = await chatsApi.shareResult(chatId, result);
      setShareUrl(res.data.share_url);
      await navigator.clipboard.writeText(res.data.share_url).catch(() => {});
    } finally {
      setSharing(false);
    }
  };

  // For guided reading: render simplified text word by word
  const renderGuidedText = () => {
    let wordIdx = 0;
    return lines.map((line, li) => {
      const clean = line.replace(/^[-•*]\s*/, "");
      const words = clean.split(/\s+/);
      const rendered = words.map((word, wi) => {
        const idx = wordIdx++;
        return (
          <span
            key={wi}
            style={idx === activeWordIdx ? {
              backgroundColor: "#FEF08A",
              borderRadius: "3px",
              padding: "0 2px",
            } : {}}
          >
            {word}{" "}
          </span>
        );
      });
      return (
        <li key={li} className="leading-relaxed max-w-reading"
          style={beelineActive ? { color: beelineColors[li % beelineColors.length], fontWeight: 500 } : {}}>
          {rendered}
        </li>
      );
    });
  };

  return (
    <div className="space-y-5">
      {/* Emoji summary */}
      {result.emoji_summary && (
        <div className="card text-center py-4">
          <p className="text-xs text-textSub mb-2 font-medium">Resumen del documento</p>
          <p className="text-4xl tracking-widest">{result.emoji_summary}</p>
        </div>
      )}

      {/* Agentic RAG — searches the agent performed */}
      {result.searches_performed && result.searches_performed.length > 0 && (
        <div className="card py-3 px-4 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-textSub shrink-0">🤖 El agente buscó:</span>
          {result.searches_performed.map((q, i) => (
            <span key={i} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
              "{q}"
            </span>
          ))}
        </div>
      )}

      {/* Simplified text */}
      <div className="card">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
          <h3 className="font-semibold text-textMain">Texto simplificado</h3>
          <div className="flex items-center gap-1.5 flex-wrap">
            {result.reading_level_used && (
              <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full font-medium">
                Nivel {result.reading_level_used}
              </span>
            )}
            {result.preset_used && (
              <span className="text-xs bg-success/10 text-green-700 px-2 py-1 rounded-full font-medium">
                {result.preset_used}
              </span>
            )}
            <button
              onClick={() => setShowComparison((v) => !v)}
              className="text-xs text-textSub border border-gray-200 px-2 py-1 rounded-full hover:border-primary/40 hover:text-primary transition-all"
            >
              {showComparison ? "🔍 Ocultar" : "🔍 Comparar"}
            </button>
            <button
              onClick={guidedActive ? stopGuidedReading : startGuidedReading}
              className={`text-xs border px-2 py-1 rounded-full transition-all ${
                guidedActive
                  ? "border-red-300 text-red-500 bg-red-50"
                  : "border-gray-200 text-textSub hover:border-primary/40 hover:text-primary"
              }`}
              title="Lectura guiada con audio"
            >
              {guidedActive ? "⏹ Detener" : "▶️ Guiada"}
            </button>
            {onExportPdf && (
              <button
                onClick={onExportPdf}
                className="text-xs text-textSub border border-gray-200 px-2 py-1 rounded-full hover:border-primary/40 hover:text-primary transition-all"
              >
                📄 PDF
              </button>
            )}
            <button
              onClick={handleShare}
              disabled={sharing}
              className="text-xs text-textSub border border-gray-200 px-2 py-1 rounded-full hover:border-primary/40 hover:text-primary transition-all"
            >
              {sharing ? "..." : "🔗 Compartir"}
            </button>
          </div>
        </div>

        {/* Share URL */}
        {shareUrl && (
          <div className="mb-3 flex items-center gap-2 bg-primary/5 border border-primary/20 rounded-xl px-3 py-2">
            <span className="text-xs text-primary flex-1 truncate">{shareUrl}</span>
            <button
              onClick={() => navigator.clipboard.writeText(shareUrl)}
              className="text-xs text-primary font-medium shrink-0"
            >
              Copiar
            </button>
          </div>
        )}

        {/* Comparison view */}
        {showComparison ? (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-textSub mb-2 uppercase tracking-wide">Original</p>
              <div className="text-sm text-textSub leading-relaxed bg-gray-50 rounded-xl p-3 max-h-64 overflow-y-auto whitespace-pre-wrap">
                {result.original_message}
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-primary mb-2 uppercase tracking-wide">Simplificado</p>
              <ul className="tdah-bullets space-y-1">
                {lines.map((line, i) => (
                  <li key={i}
                    style={beelineActive ? { color: beelineColors[i % beelineColors.length], fontWeight: 500 } : {}}
                    className="leading-relaxed text-sm"
                  >
                    {line.replace(/^[-•*]\s*/, "")}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : guidedActive ? (
          <ul className="space-y-2">{renderGuidedText()}</ul>
        ) : (
          <ul className="space-y-2">
            {lines.map((line, i) => {
              const clean = line.replace(/^[-•*]\s*/, "");
              return (
                <li
                  key={i}
                  className="flex items-start gap-2 group leading-relaxed max-w-reading"
                  style={beelineActive ? { color: beelineColors[i % beelineColors.length], fontWeight: 500 } : {}}
                >
                  <span className="flex-1">{clean}</span>
                  <button
                    onClick={() => speakLine(clean)}
                    title="Escuchar esta línea"
                    className="opacity-0 group-hover:opacity-100 text-xs text-textSub hover:text-primary transition-all shrink-0 mt-0.5"
                  >
                    🔊
                  </button>
                </li>
              );
            })}
          </ul>
        )}

        {result.audio_url && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-textSub mb-2">🔊 Escuchar</p>
            <audio controls src={result.audio_url} className="w-full" />
          </div>
        )}
      </div>

      {/* Glossary */}
      {result.glossary && result.glossary.length > 0 && (
        <details className="card cursor-pointer group">
          <summary className="flex items-center justify-between font-medium text-textMain list-none">
            <span>📚 Glosario de términos</span>
            <span className="text-textSub text-sm group-open:rotate-180 transition-transform">▾</span>
          </summary>
          <div className="mt-3 space-y-2">
            {result.glossary.map((entry, i) => (
              <div key={i} className="flex gap-3 text-sm">
                <span className="font-semibold text-primary shrink-0">{entry.word}:</span>
                <span className="text-textSub leading-relaxed">{entry.definition}</span>
              </div>
            ))}
          </div>
        </details>
      )}

      {/* Concept map */}
      <ConceptMap simplifiedText={result.simplified_text} chatId={chatId} />

      {/* Explanation */}
      <details className="card cursor-pointer group">
        <summary className="flex items-center justify-between font-medium text-textMain list-none">
          <span>💬 ¿Por qué cambié esto?</span>
          <span className="text-textSub text-sm group-open:rotate-180 transition-transform">▾</span>
        </summary>
        <p className="text-textSub mt-3 leading-relaxed text-sm max-w-reading">
          {result.explanation}
        </p>
      </details>

      {/* Comprehension quiz */}
      <ComprehensionQuiz
        simplifiedText={result.simplified_text}
        chatId={chatId}
        onResimplify={onResimplify}
      />

      {/* WCAG badge */}
      <WcagBadge report={result.wcag_report} />
    </div>
  );
}
