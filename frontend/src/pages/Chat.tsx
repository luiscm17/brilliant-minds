import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { chatsApi } from "../api/endpoints";
import type { SimplifiedResponse } from "../api/endpoints";
import SimplifiedView from "../components/SimplifiedView";
import AccessibilityBar from "../components/AccessibilityBar";
import PomodoroTimer from "../components/PomodoroTimer";
import VersionTabs from "../components/VersionTabs";
import { useAuthStore } from "../store/auth";
import { useChatStore } from "../store/chat";
import { jsPDF } from "jspdf";

export default function Chat() {
  const [searchParams] = useSearchParams();
  const docId = searchParams.get("doc");
  const titleParam = searchParams.get("title");

  const [chatId, setChatId] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<SimplifiedResponse | null>(null);
  const [docenteResults, setDocenteResults] = useState<SimplifiedResponse[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const [fatigueLevel, setFatigueLevel] = useState(0);
  const [targetLanguage, setTargetLanguage] = useState("");
  const [isListening, setIsListening] = useState(false);

  const navigate = useNavigate();
  const { profile } = useAuthStore();
  const { addMessage, getMessages, chats, setChats } = useChatStore();
  const isDocente = profile?.preset === "Docente";
  const isTDAH = profile?.preset === "TDAH";
  const history = chatId ? getMessages(chatId) : [];

  // Create chat session on mount with auto-title from filename
  useEffect(() => {
    const title = titleParam ? decodeURIComponent(titleParam) : "Nueva simplificación";
    chatsApi.create(title).then((res) => setChatId(res.data.chat_id));
    chatsApi.list().then((res) => setChats(res.data)).catch(() => {});
  }, []);

  const handleResimplify = () => {
    setFatigueLevel((prev) => Math.min(prev + 1, 2));
    setResult(null);
    setTimeout(() => handleSend(), 50);
  };

  const exportPdf = () => {
    if (!result) return;
    const doc = new jsPDF();
    const title = titleParam ? decodeURIComponent(titleParam) : "Documento simplificado";
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text(title, 15, 20);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    if (result.reading_level_used) {
      doc.setTextColor(91, 141, 239);
      doc.text(`Nivel ${result.reading_level_used}  |  ${result.preset_used ?? ""}`, 15, 30);
      doc.setTextColor(0, 0, 0);
    }
    const lines = doc.splitTextToSize(result.simplified_text, 180);
    doc.text(lines, 15, 42);
    if (result.glossary && result.glossary.length > 0) {
      let y = 42 + lines.length * 6 + 10;
      doc.setFont("helvetica", "bold");
      doc.text("Glosario", 15, y); y += 8;
      doc.setFont("helvetica", "normal");
      result.glossary.forEach((entry) => {
        const entry_text = `• ${entry.word}: ${entry.definition}`;
        const wrapped = doc.splitTextToSize(entry_text, 180);
        doc.text(wrapped, 15, y);
        y += wrapped.length * 6 + 2;
      });
    }
    doc.save(`${title}.pdf`);
  };

  const startVoiceInput = () => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SR) { alert("Tu navegador no soporta dictado por voz. Usa Chrome."); return; }
    const recognition = new SR();
    recognition.lang = targetLanguage === "english" ? "en-US" : "es-ES";
    recognition.interimResults = false;
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (e: any) => setMessage((prev) => prev + e.results[0][0].transcript);
    recognition.start();
  };

  const handleSend = async () => {
    if (!chatId || !message.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    setDocenteResults(null);
    const lang = targetLanguage || undefined;
    try {
      if (isDocente) {
        const levels = ["A1", "A2", "B1"];
        const responses = await Promise.all(
          levels.map((level) =>
            chatsApi.sendMessage(chatId, `[Nivel ${level}] ${message}`, docId ? [docId] : undefined, fatigueLevel, lang)
          )
        );
        setDocenteResults(responses.map((r) => r.data));
      } else {
        const res = await chatsApi.sendMessage(chatId, message, docId ? [docId] : undefined, fatigueLevel, lang);
        setResult(res.data);
        addMessage(chatId, { role: "user", text: message, timestamp: new Date().toISOString() });
        addMessage(chatId, { role: "assistant", text: res.data.simplified_text, result: res.data, timestamp: new Date().toISOString() });
      }
    } catch {
      setError("Algo salió diferente. ¿Intentamos de nuevo?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg flex flex-col pb-24">
      {/* Sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-20"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      {sidebarOpen && (
        <aside style={{ position: "fixed", top: 0, left: 0, height: "100%", width: "280px", backgroundColor: "#F8F7F4", borderRight: "1px solid #e5e7eb", boxShadow: "4px 0 16px rgba(0,0,0,0.12)", zIndex: 30, display: "flex", flexDirection: "column" }}>
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
            <span className="font-semibold text-textMain">Historial de chats</span>
            <button onClick={() => setSidebarOpen(false)} className="text-textSub hover:text-textMain text-xl leading-none">✕</button>
          </div>
          <div style={{ flex: 1, overflowY: "auto" }} className="py-2">
            {chats.length === 0 ? (
              <p className="text-textSub text-sm px-5 py-6 text-center">Aún no tienes chats anteriores.</p>
            ) : (
              chats.map((chat: any) => {
                const id = chat.chat_id;
                const isActive = id === chatId;
                const isEditing = editingChatId === id;

                const saveTitle = async () => {
                  if (!editingTitle.trim()) return setEditingChatId(null);
                  try {
                    await chatsApi.updateTitle(id, editingTitle.trim());
                    setChats(chats.map((c: any) => c.chat_id === id ? { ...c, title: editingTitle.trim() } : c));
                    setEditingChatId(null);
                  } catch {
                    alert("No se pudo guardar el título. Intenta de nuevo.");
                  }
                };

                return (
                  <div
                    key={id}
                    style={isActive ? { backgroundColor: "#EBF2FF", borderLeft: "3px solid #5B8DEF" } : {}}
                    className="border-b border-gray-100 group"
                  >
                    {isEditing ? (
                      <div className="px-4 py-2 flex gap-2 items-center">
                        <input
                          autoFocus
                          className="input text-sm py-1 flex-1"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => { if (e.key === "Enter") saveTitle(); if (e.key === "Escape") setEditingChatId(null); }}
                        />
                        <button onClick={saveTitle} className="text-primary text-sm font-medium">✓</button>
                        <button onClick={() => setEditingChatId(null)} className="text-textSub text-sm">✕</button>
                      </div>
                    ) : (
                      <div className="flex items-center px-2 hover:bg-blue-50 transition-colors">
                        <button
                          onClick={() => { navigate(`/chat/${id}`); setSidebarOpen(false); }}
                          className="flex-1 text-left px-3 py-3"
                        >
                          <p className="text-sm font-medium text-textMain truncate">{chat.title}</p>
                          <p className="text-xs text-textSub mt-0.5">
                            {new Date(chat.created_at).toLocaleDateString("es-ES", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
                          </p>
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); setEditingChatId(id); setEditingTitle(chat.title); }}
                          className="opacity-0 group-hover:opacity-100 p-2 text-textSub hover:text-primary transition-all text-xs"
                          title="Renombrar"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={async (e) => {
                            e.stopPropagation();
                            if (!confirm("¿Eliminar este chat?")) return;
                            await chatsApi.deleteChat(id);
                            setChats(chats.filter((c: any) => c.chat_id !== id));
                            if (id === chatId) { setChatId(null); setResult(null); }
                          }}
                          className="opacity-0 group-hover:opacity-100 p-2 text-textSub hover:text-red-400 transition-all text-xs"
                          title="Eliminar"
                        >
                          🗑️
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
          <div className="p-4 border-t border-gray-200">
            <button onClick={() => { navigate("/dashboard"); setSidebarOpen(false); }} className="btn-secondary w-full text-sm py-2">
              ← Inicio
            </button>
          </div>
        </aside>
      )}

      {/* Header */}
      <header className="bg-surface border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <button
          onClick={() => { setSidebarOpen(true); chatsApi.list().then((res) => setChats(res.data)).catch(() => {}); }}
          className="text-textSub hover:text-textMain p-1 rounded-lg hover:bg-gray-100 transition-colors"
          title="Ver historial de chats"
        >
          ☰
        </button>
        <button onClick={() => navigate("/dashboard")} className="text-textSub hover:text-textMain text-xl">
          ←
        </button>
        <div className="min-w-0 flex-1">
          <h1 className="text-base font-semibold text-textMain leading-tight truncate">
            {titleParam ? decodeURIComponent(titleParam) : "Simplificar documento"}
          </h1>
          <p className="text-xs text-textSub">El agente adapta el texto a tu perfil</p>
        </div>
      </header>

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-6 space-y-6">
        {/* Chat history */}
        {history.length > 0 && !result && !loading && (
          <div className="space-y-3">
            {history.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-sm px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-primary text-white rounded-br-sm"
                    : "bg-surface text-textMain rounded-bl-sm"
                }`}>
                  {msg.text.length > 120 ? msg.text.slice(0, 120) + "..." : msg.text}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Steps indicator */}
        {!result && !loading && (
          <div className="card">
            <p className="text-sm font-medium text-textMain mb-3">¿Qué quieres hacer?</p>
            <div className="space-y-2">
              {[
                "Simplifica este documento",
                "Resume los puntos más importantes",
                "Explícame el capítulo 1",
                "¿Cuáles son las fechas importantes?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setMessage(suggestion)}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm border transition-all ${
                    message === suggestion
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-gray-200 text-textSub hover:border-primary/40 hover:text-textMain"
                  }`}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input area */}
        {!result && (
          <div className="card space-y-3">
            {/* Fatigue selector */}
            <div>
              <p className="text-xs font-medium text-textSub mb-2">¿Cómo te sientes hoy?</p>
              <div className="flex gap-2">
                {[
                  { level: 0, label: "Bien", emoji: "😊" },
                  { level: 1, label: "Cansado", emoji: "😴" },
                  { level: 2, label: "Muy cansado", emoji: "🥱" },
                ].map(({ level, label, emoji }) => (
                  <button
                    key={level}
                    onClick={() => setFatigueLevel(level)}
                    className={`flex-1 py-2 rounded-xl text-xs border transition-all ${
                      fatigueLevel === level
                        ? "border-primary bg-primary/10 text-primary font-semibold"
                        : "border-gray-200 text-textSub hover:border-primary/40"
                    }`}
                  >
                    {emoji} {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Language selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-textSub font-medium whitespace-nowrap">🌐 Idioma salida:</span>
              <select
                className="input text-sm py-1 flex-1"
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
              >
                <option value="">Auto-detectar</option>
                <option value="español">Español</option>
                <option value="english">English</option>
                <option value="português">Português</option>
                <option value="français">Français</option>
                <option value="deutsch">Deutsch</option>
              </select>
            </div>

            <label className="block text-sm font-medium text-textSub">
              O escribe tu instrucción:
            </label>
            <div className="relative">
              <textarea
                className="input resize-none pr-12"
                rows={3}
                placeholder="Ej: Simplifica el contrato con frases cortas y bullets..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
              <button
                type="button"
                onClick={startVoiceInput}
                title="Dictar por voz"
                className={`absolute bottom-3 right-3 text-lg p-1 rounded-full transition-all ${
                  isListening ? "text-red-500 animate-pulse" : "text-textSub hover:text-primary"
                }`}
              >
                🎙️
              </button>
            </div>
            <button
              onClick={handleSend}
              disabled={loading || !message.trim() || !chatId}
              className="btn-primary w-full"
            >
              {loading ? "El agente está trabajando..." : "Simplificar →"}
            </button>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="card text-center py-10 space-y-3">
            <div className="text-4xl animate-pulse">🤖</div>
            <p className="font-medium text-textMain">Estoy simplificando tu documento...</p>
            <p className="text-textSub text-sm">Esto toma unos segundos</p>
            <div className="flex justify-center gap-1 mt-2">
              {["Analizando", "Simplificando", "Revisando tono", "Validando"].map((step) => (
                <span key={step} className="text-xs bg-surface px-2 py-1 rounded-full text-textSub">
                  {step}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-warning/10 border border-warning/30 text-warning rounded-xl px-4 py-3 text-sm flex items-center gap-2">
            <span>💡</span> {error}
            <button onClick={handleSend} className="ml-auto underline">Reintentar</button>
          </div>
        )}

        {/* Result — normal */}
        {result && (
          <>
            <SimplifiedView
              result={result}
              chatId={chatId ?? ""}
              onResimplify={handleResimplify}
              onExportPdf={exportPdf}
            />
            <button
              onClick={() => { setResult(null); setMessage(""); }}
              className="btn-secondary w-full"
            >
              Hacer otra pregunta
            </button>
          </>
        )}

        {/* Result — Docente multi-versiones */}
        {docenteResults && (
          <>
            <VersionTabs results={docenteResults} />
            <button
              onClick={() => { setDocenteResults(null); setMessage(""); }}
              className="btn-secondary w-full"
            >
              Generar otras versiones
            </button>
          </>
        )}
      </main>

      <AccessibilityBar />
      {isTDAH && (result || docenteResults) && <PomodoroTimer />}
    </div>
  );
}
