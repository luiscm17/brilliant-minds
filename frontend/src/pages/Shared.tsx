import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { sharedApi } from "../api/endpoints";
import type { SimplifiedResponse } from "../api/endpoints";
import WcagBadge from "../components/WcagBadge";

export default function Shared() {
  const { token } = useParams<{ token: string }>();
  const [result, setResult] = useState<SimplifiedResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!token) return;
    sharedApi.get(token)
      .then((res) => setResult(res.data))
      .catch(() => setError(true));
  }, [token]);

  if (error) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center px-4">
        <div className="card text-center max-w-sm w-full py-12 space-y-3">
          <p className="text-4xl">🔗</p>
          <h1 className="font-bold text-textMain">Link no encontrado</h1>
          <p className="text-textSub text-sm">Este enlace no existe o ya expiró.</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="text-textSub animate-pulse">Cargando resultado compartido...</p>
      </div>
    );
  }

  const lines = result.simplified_text.split(/\r?\n/).filter((l) => l.trim());

  return (
    <div className="min-h-screen bg-bg pb-16">
      <header className="bg-surface border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📄</span>
          <div>
            <h1 className="font-bold text-textMain">DocSimplify</h1>
            <p className="text-xs text-textSub">Documento simplificado compartido</p>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6 space-y-5">
        {result.emoji_summary && (
          <div className="card text-center py-4">
            <p className="text-xs text-textSub mb-2 font-medium">Resumen</p>
            <p className="text-4xl tracking-widest">{result.emoji_summary}</p>
          </div>
        )}

        <div className="card">
          <div className="flex items-center gap-2 mb-4 flex-wrap">
            <h2 className="font-semibold text-textMain flex-1">Texto simplificado</h2>
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
          </div>
          <ul className="tdah-bullets space-y-2">
            {lines.map((line, i) => (
              <li key={i} className="leading-relaxed">
                {line.replace(/^[-•*]\s*/, "")}
              </li>
            ))}
          </ul>
        </div>

        {result.glossary && result.glossary.length > 0 && (
          <details className="card cursor-pointer">
            <summary className="font-medium text-textMain list-none">📚 Glosario de términos</summary>
            <div className="mt-3 space-y-2">
              {result.glossary.map((entry, i) => (
                <div key={i} className="flex gap-3 text-sm">
                  <span className="font-semibold text-primary shrink-0">{entry.word}:</span>
                  <span className="text-textSub">{entry.definition}</span>
                </div>
              ))}
            </div>
          </details>
        )}

        <WcagBadge report={result.wcag_report} />

        <div className="card text-center py-4 space-y-2">
          <p className="text-sm text-textSub">¿Quieres simplificar tus propios documentos?</p>
          <a
            href="/"
            className="btn-primary inline-block text-sm px-6 py-2"
          >
            Probar DocSimplify gratis →
          </a>
        </div>
      </main>
    </div>
  );
}
