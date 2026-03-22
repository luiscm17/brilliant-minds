"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import BeforeAfterPreview from "../../components/BeforeAfterPreview";
import { createChat, listDocuments, sendChatMessage } from "../../lib/api";
import { useUser } from "../../context/UserContext";
import type { ChatMessage, DocumentItem } from "../../lib/types";

const promptSuggestions = [
  "Simplifica este texto en nivel A2",
  "Explicame este contrato con bullets calmados",
  "Resume los puntos clave para una persona con TDAH",
];

const CHAT_STORAGE_KEY = "active_chat_id";

export default function Chat() {
  const router = useRouter();
  const { isAuthenticated, profile } = useUser();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatId, setChatId] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    if (!profile) {
      router.replace("/onboarding");
    }
  }, [isAuthenticated, profile, router]);

  useEffect(() => {
    async function prepareChat() {
      const savedChatId =
        typeof window !== "undefined"
          ? window.localStorage.getItem(CHAT_STORAGE_KEY)
          : null;

      if (savedChatId) {
        setChatId(savedChatId);
      } else {
        try {
          const createdChat = await createChat("Hackathon demo");
          setChatId(createdChat.chatId);
          if (typeof window !== "undefined") {
            window.localStorage.setItem(CHAT_STORAGE_KEY, createdChat.chatId);
          }
        } catch {
          setError("No fue posible iniciar un chat nuevo.");
        }
      }

      try {
        const nextDocuments = await listDocuments();
        setDocuments(nextDocuments);
      } catch {
        setDocuments([]);
      }
    }

    if (isAuthenticated && profile) {
      void prepareChat();
    }
  }, [isAuthenticated, profile]);

  const handleSend = async (nextInput?: string) => {
    const trimmedInput = (nextInput ?? input).trim();

    if (!trimmedInput || !profile || !chatId) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      text: trimmedInput,
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setInput("");
    setError(null);
    setIsSending(true);

    try {
      const response = await sendChatMessage(chatId, {
        message: trimmedInput,
        documentIds: documents.map((document) => document.documentId),
      });
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        data: response,
      };

      setMessages((currentMessages) => [...currentMessages, assistantMessage]);
    } catch {
      setError(
        "No fue posible obtener respuesta del asistente. Intenta nuevamente.",
      );
    } finally {
      setIsSending(false);
    }
  };

  if (!isAuthenticated || !profile) {
    return null;
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="studio-panel w-full p-5 md:p-8"
    >
      <div className="grid gap-6 xl:grid-cols-[0.74fr_1.26fr]">
        <motion.aside
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.08, duration: 0.4 }}
          className="rounded-[28px] bg-[linear-gradient(180deg,rgba(255,255,255,0.82),rgba(248,241,230,0.76))] p-6"
        >
          <span className="eyebrow">Conversation Lab</span>
          <h1 className="display-title mt-5 text-5xl xl:text-6xl">
            habla
            <br />
            con claridad
          </h1>
          <p className="muted-copy mt-5 text-base leading-7">
            Este espacio debe sentirse tranquilo, rapido y muy facil de leer.
            Usa prompts cortos y muestra una respuesta clara, calmada y util.
          </p>

          <div className="mt-8 space-y-3">
            {promptSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => handleSend(suggestion)}
                className="ghost-button w-full justify-start text-left"
              >
                {suggestion}
              </button>
            ))}
          </div>

          <div className="mt-8 rounded-[24px] bg-[rgba(13,122,116,0.08)] p-4">
            <p className="text-sm uppercase tracking-[0.14em] text-[var(--teal-deep)]">
              Perfil activo
            </p>
            <p className="mt-2 text-xl font-semibold text-slate-800">
              {profile.preset} / {profile.readingLevel}
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Ajustado para {profile.hasAdhd ? "TDAH" : "enfoque general"}
              {profile.hasDyslexia ? " y dislexia" : ""}.
            </p>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Chat activo: {chatId ? chatId.slice(0, 8) : "creando..."}.
              Documentos disponibles: {documents.length}.
            </p>
          </div>

          <div className="mt-6 rounded-[24px] bg-white/70 p-4">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
              Accesibilidad aplicada
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="status-pill">Preset {profile.preset}</span>
              <span className="status-pill">Nivel {profile.readingLevel}</span>
              <span className="status-pill">
                Frases {profile.maxSentenceLength}
              </span>
            </div>
          </div>
        </motion.aside>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.14, duration: 0.4 }}
          className="rounded-[28px] bg-[rgba(255,250,242,0.72)] p-4 md:p-5"
        >
          <div className="flex items-center justify-between px-2 pb-4">
            <span className="eyebrow">Chat IA</span>
            <span className="status-pill">
              {isSending ? "Procesando" : chatId ? "Listo" : "Creando chat"}
            </span>
          </div>

          <div className="min-h-[26rem] space-y-4 rounded-[24px] bg-[rgba(255,255,255,0.56)] p-4 md:p-5">
            {messages.length === 0 ? (
              <div className="rounded-[24px] border border-dashed border-[rgba(23,49,59,0.14)] bg-white/60 p-6">
                <p className="text-lg font-semibold text-slate-800">
                  Aun no hay mensajes
                </p>
                <p className="mt-2 max-w-xl text-sm leading-7 text-slate-600">
                  Prueba una de las sugerencias o escribe una instruccion
                  concreta para mostrar el valor del sistema en la demo.
                </p>
              </div>
            ) : (
              <AnimatePresence initial={false}>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 18 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.24 }}
                    className={
                      message.role === "user"
                        ? "message-bubble-user"
                        : "message-bubble-ai"
                    }
                  >
                    {message.role === "user" ? (
                      <p className="leading-7">{message.text}</p>
                    ) : (
                      <>
                        <p className="leading-7 text-slate-800">
                          {message.data.simplifiedText}
                        </p>
                        <p className="mt-3 border-t border-slate-200 pt-3 text-sm leading-6 text-slate-500">
                          {message.data.explanation}
                        </p>
                      </>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
          </div>

          {error ? (
            <div className="mt-4 rounded-2xl bg-[rgba(222,123,89,0.14)] p-4 text-sm text-[#96472f]">
              {error}
            </div>
          ) : null}

          <div className="mt-5 flex flex-col gap-3 md:flex-row">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu mensaje"
              className="app-input flex-1"
            />
            <button
              onClick={() => handleSend()}
              disabled={isSending || input.trim().length === 0 || !chatId}
              className="primary-button md:min-w-[10rem]"
            >
              {isSending ? "Enviando..." : "Enviar"}
            </button>
          </div>

          <div className="mt-6">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
              Antes vs despues de una respuesta
            </p>
            <div className="mt-4">
              <BeforeAfterPreview
                preset={profile.preset}
                readingLevel={profile.readingLevel}
                maxSentenceLength={profile.maxSentenceLength}
              />
            </div>
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
}
