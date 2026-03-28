"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import BeforeAfterPreview from "../../components/BeforeAfterPreview";
import ChatResultCard from "../../components/ChatResultCard";
import PipelineTimeline from "../../components/PipelineTimeline";
import {
  createChat,
  listDocuments,
  sendAgentMessage,
  sendChatMessage,
} from "../../lib/api";
import { useUser } from "../../context/UserContext";
import { getPaletteLabel, readExperienceDraft } from "../../lib/profile";
import type { ChatMessage, ChatResponse, DocumentItem } from "../../lib/types";

const promptSuggestions = [
  "Simplifica este texto en nivel A2",
  "Explicame este contrato con bullets calmados",
  "Resume los puntos clave con una lectura mas estable",
];

const CHAT_STORAGE_KEY = "active_chat_id";
const DEMO_PROMPT =
  "Simplifica este contrato en nivel A2, marca puntos urgentes y explica los cambios.";

function ChatPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, profile } = useUser();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatId, setChatId] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [immersiveMode, setImmersiveMode] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [fatigueLevel, setFatigueLevel] = useState(0);
  const [targetLanguage, setTargetLanguage] = useState("");
  const [chatMode, setChatMode] = useState<"rag" | "agent">("rag");
  const [chatBooting, setChatBooting] = useState(true);
  const stageTimeoutsRef = useRef<number[]>([]);
  const activeStreamRef = useRef(0);
  const hasAssistantMessage = messages.some((message) => message.role === "assistant");

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
      setChatBooting(true);
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
      } finally {
        setChatBooting(false);
      }
    }

    if (isAuthenticated && profile) {
      void prepareChat();
    }
  }, [isAuthenticated, profile]);

  useEffect(() => {
    const hasProcessingDocuments = documents.some(
      (document) => document.status === "processing",
    );

    if (!hasProcessingDocuments || !isAuthenticated || !profile) {
      return;
    }

    const intervalId = window.setInterval(async () => {
      try {
        setDocuments(await listDocuments());
      } catch {
        // Keep the current list if polling fails transiently.
      }
    }, 12000);

    return () => window.clearInterval(intervalId);
  }, [documents, isAuthenticated, profile]);

  useEffect(() => {
    setSelectedDocumentIds((currentSelected) =>
      currentSelected.filter((documentId) =>
        documents.some(
          (document) =>
            document.documentId === documentId && document.status === "completed",
        ),
      ),
    );
  }, [documents]);

  useEffect(() => {
    return () => {
      stageTimeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
      stageTimeoutsRef.current = [];
      activeStreamRef.current += 1;
    };
  }, []);

  useEffect(() => {
    if (searchParams.get("demo") === "1" && chatId && messages.length === 0) {
      void handleSend(DEMO_PROMPT);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatId, searchParams, messages.length]);

  const pushAssistantMessage = async (response: ChatResponse) => {
    const assistantMessageId = crypto.randomUUID();
    const finalText = response.simplifiedText;
    const streamId = activeStreamRef.current + 1;
    const chunkSize = Math.max(28, Math.ceil(finalText.length / 6));

    activeStreamRef.current = streamId;

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: assistantMessageId,
        role: "assistant",
        data: {
          ...response,
          simplifiedText: "",
        },
      },
    ]);

    for (let index = chunkSize; index < finalText.length; index += chunkSize) {
      if (activeStreamRef.current !== streamId) {
        return;
      }

      await new Promise((resolve) => setTimeout(resolve, 30));

      if (activeStreamRef.current !== streamId) {
        return;
      }

      setMessages((currentMessages) =>
        currentMessages.map((message) =>
          message.id === assistantMessageId && message.role === "assistant"
            ? {
                ...message,
                data: {
                  ...message.data,
                  simplifiedText: finalText.slice(0, index),
                },
              }
            : message,
        ),
      );
    }

    if (activeStreamRef.current !== streamId) {
      return;
    }

    setMessages((currentMessages) =>
      currentMessages.map((message) =>
        message.id === assistantMessageId && message.role === "assistant"
          ? {
              ...message,
              data: {
                ...message.data,
                simplifiedText: finalText,
              },
            }
          : message,
      ),
    );
  };

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
    setProcessingStage(1);

    try {
      activeStreamRef.current += 1;
      stageTimeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
      stageTimeoutsRef.current = [];

      const stageDelays = [0, 220, 520];
      stageTimeoutsRef.current = stageDelays.slice(1).map((delay, index) =>
        window.setTimeout(() => {
          setProcessingStage(index + 2);
        }, delay),
      );

      const payload = {
        message: trimmedInput,
        documentIds:
          selectedDocumentIds.length > 0 ? selectedDocumentIds : undefined,
        fatigueLevel,
        targetLanguage: targetLanguage || null,
      };

      const response =
        chatMode === "agent"
          ? await sendAgentMessage(payload)
          : await sendChatMessage(chatId, payload);

      setProcessingStage(4);
      await pushAssistantMessage(response);
    } catch {
      setError(
        "No fue posible obtener respuesta del asistente. Intenta nuevamente.",
      );
    } finally {
      stageTimeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
      stageTimeoutsRef.current = [];
      setIsSending(false);
      window.setTimeout(() => setProcessingStage(0), 600);
    }
  };

  if (!isAuthenticated || !profile) {
    return null;
  }

  const paletteLabel = getPaletteLabel(readExperienceDraft().palettePreference);
  const completedDocuments = documents.filter(
    (document) => document.status === "completed",
  );

  const toggleDocumentSelection = (documentId: string) => {
    setSelectedDocumentIds((currentSelected) =>
      currentSelected.includes(documentId)
        ? currentSelected.filter((currentId) => currentId !== documentId)
        : [...currentSelected, documentId],
    );
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className={immersiveMode ? "w-full" : "studio-panel hero-grid w-full p-5 md:p-8"}
    >
      <div
        className={
          immersiveMode
            ? "mx-auto max-w-5xl space-y-6 rounded-[32px] border border-[rgba(23,49,59,0.08)] bg-[rgba(255,255,255,0.92)] p-6 shadow-[0_30px_80px_rgba(23,49,59,0.12)]"
            : "grid gap-6 xl:grid-cols-[0.74fr_1.26fr]"
        }
      >
        {!immersiveMode ? (
          <motion.aside
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.08, duration: 0.4 }}
            className="dark-studio-panel rounded-[28px] p-6 text-white"
          >
            <span className="eyebrow">Conversation Lab</span>
            <h1 className="display-title mt-5 text-5xl xl:text-6xl">
              habla
              <br />
              con claridad
            </h1>
            <p className="reading-copy mt-5 text-base leading-8 text-white/84">
              Empieza con una instruccion breve y deja que la interfaz muestre
              una respuesta mas clara, calmada y facil de seguir.
            </p>

            <div className="mt-8 space-y-3">
              {promptSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSend(suggestion)}
                  className="secondary-button w-full justify-start border-white/10 bg-white/10 text-left text-white"
                >
                  {suggestion}
                </button>
              ))}
            </div>

            <div className="mt-8 rounded-[24px] border border-white/12 bg-white/8 p-4">
              <p className="text-sm uppercase tracking-[0.14em] text-white/58">
                Estilo activo
              </p>
              <p className="mt-2 text-xl font-semibold text-white">
                {paletteLabel} - {profile.readingLevel}
              </p>
              <p className="mt-2 text-sm leading-6 text-white/80">
                Ajustado para una lectura mas clara, calmada y facil de seguir.
              </p>
              <p className="mt-3 text-sm leading-6 text-white/70">
                Chat activo: {chatId ? chatId.slice(0, 8) : "creando..."}.
                Documentos disponibles: {documents.length}.
              </p>
            </div>

            <div className="mt-6 rounded-[24px] border border-white/12 bg-white/8 p-4">
              <p className="text-sm uppercase tracking-[0.14em] text-white/58">
                Contexto para el chat
              </p>
              {completedDocuments.length === 0 ? (
                <p className="mt-3 text-sm leading-6 text-white/72">
                  Aun no hay documentos listos. Puedes conversar igual, pero la
                  mejor demo aparece cuando ya hay material preparado.
                </p>
              ) : (
                <div className="mt-3 flex flex-wrap gap-2">
                  {completedDocuments.map((document) => {
                    const isSelected = selectedDocumentIds.includes(document.documentId);
                    return (
                      <button
                        key={document.documentId}
                        onClick={() => toggleDocumentSelection(document.documentId)}
                        className={
                          isSelected
                            ? "primary-button px-3 py-2 text-sm"
                            : "secondary-button border-white/10 bg-white/10 px-3 py-2 text-sm text-white"
                        }
                      >
                        {document.filename}
                      </button>
                    );
                  })}
                </div>
              )}
              <p className="mt-3 text-sm leading-6 text-white/70">
                Seleccionados: {selectedDocumentIds.length}. Si no eliges ninguno,
                el mensaje se enviara sin apoyo documental.
              </p>
            </div>
          </motion.aside>
        ) : null}

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.14, duration: 0.4 }}
          className="rounded-[28px] border border-white/12 bg-[rgba(13,19,28,0.88)] p-4 md:p-5"
        >
          <div className="flex flex-wrap items-center justify-between gap-3 px-2 pb-4">
            <div className="flex items-center gap-2">
              <span className="eyebrow">Chat IA</span>
              <span className="status-pill">
                {isSending ? "Procesando" : chatId ? "Listo" : "Creando chat"}
              </span>
              <span className="status-pill">
                {chatMode === "agent" ? "Modo agente" : "Modo RAG"}
              </span>
            </div>

            <button
              onClick={() => setImmersiveMode((current) => !current)}
              className="secondary-button px-4 py-2 text-sm"
            >
              {immersiveMode ? "Salir de foco" : "Modo inmersivo"}
            </button>
          </div>

          <div className="mb-5">
            <PipelineTimeline
              steps={[
                {
                  title: "Analizando mensaje",
                  description: "El agente identifica tono, nivel y objetivo.",
                  state: processingStage >= 1 ? "done" : "idle",
                },
                {
                  title: "Consultando contexto",
                  description: "Usa documentos cargados para grounding.",
                  state:
                    processingStage === 2
                      ? "active"
                      : processingStage > 2
                        ? "done"
                        : "idle",
                },
                {
                  title: "Aplicando accesibilidad",
                  description:
                    "Reduce carga cognitiva y ajusta el tono de salida.",
                  state:
                    processingStage === 3
                      ? "active"
                      : processingStage > 3
                        ? "done"
                        : "idle",
                },
                {
                  title: "Generando respuesta",
                  description: "Entrega una respuesta explicable y adaptada.",
                  state: processingStage >= 4 ? "active" : "idle",
                },
              ]}
            />
          </div>

          <div className="min-h-[26rem] space-y-4 rounded-[24px] border border-white/10 bg-[rgba(255,255,255,0.07)] p-4 md:p-5">
            {chatBooting ? (
              <div className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
                <div className="rounded-[24px] border border-white/10 bg-white/8 p-6">
                  <div className="skeleton-block h-5 w-40" />
                  <div className="mt-4 space-y-3">
                    <div className="skeleton-block h-4 w-full" />
                    <div className="skeleton-block h-4 w-[85%]" />
                    <div className="skeleton-block h-4 w-[70%]" />
                  </div>
                </div>
                <div className="rounded-[24px] border border-white/10 bg-white/8 p-5">
                  <div className="skeleton-block h-5 w-32" />
                  <div className="mt-4 space-y-3">
                    <div className="skeleton-block h-4 w-[92%]" />
                    <div className="skeleton-block h-4 w-[76%]" />
                    <div className="skeleton-block h-4 w-[84%]" />
                  </div>
                </div>
              </div>
            ) : messages.length === 0 ? (
              <div className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
                <div className="rounded-[24px] border border-dashed border-[rgba(76,226,244,0.28)] bg-white/8 p-6">
                  <p className="text-lg font-semibold text-white">
                    Todo listo para empezar
                  </p>
                  <p className="reading-copy mt-2 text-sm leading-7 text-white/76">
                    Usa una sugerencia, abre la demo guiada o escribe una
                    pregunta concreta para mostrar el valor del sistema.
                  </p>
                </div>
                <div className="rounded-[24px] border border-white/10 bg-white/8 p-5">
                  <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
                    Recorrido sugerido
                  </p>
                  <div className="mt-4 space-y-3 text-sm leading-7 text-white/74">
                    <p>1. El agente identifica nivel, tono y objetivo.</p>
                    <p>2. Usa tus documentos como contexto.</p>
                    <p>3. Entrega una respuesta mas clara y explicable.</p>
                  </div>
                </div>
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
                      <ChatResultCard chatId={chatId} response={message.data} />
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
          </div>

          {error ? (
            <div className="mt-4 rounded-2xl border border-[rgba(255,125,108,0.22)] bg-[rgba(255,125,108,0.12)] p-4 text-sm text-[#ffd2cb]">
              {error}
            </div>
          ) : null}

          <div className="mt-4 flex flex-wrap gap-2">
            <span className="status-pill">{paletteLabel}</span>
            <span className="status-pill">Nivel {profile.readingLevel}</span>
            <span className="status-pill">Frases {profile.maxSentenceLength}</span>
            <span className="status-pill">Docs {documents.length}</span>
            <span className="status-pill">Fatiga {fatigueLevel}</span>
            <button
              onClick={() =>
                setChatMode((current) => (current === "rag" ? "agent" : "rag"))
              }
              className="secondary-button px-4 py-2 text-sm"
            >
              {chatMode === "rag" ? "Cambiar a agente" : "Cambiar a RAG"}
            </button>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-[0.78fr_0.22fr]">
            <div className="rounded-[24px] border border-white/10 bg-white/8 p-3">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/60">
                Carga cognitiva hoy
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {[0, 1, 2].map((value) => (
                  <button
                    key={value}
                    onClick={() => setFatigueLevel(value)}
                    className={
                      fatigueLevel === value
                        ? "secondary-button px-4 py-2 text-sm"
                        : "ghost-button px-4 py-2 text-sm"
                    }
                  >
                    {value === 0 ? "Bien" : value === 1 ? "Cansado" : "Muy cansado"}
                  </button>
                ))}
              </div>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/8 p-3">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/60">
                Idioma de salida
              </p>
              <select
                value={targetLanguage}
                onChange={(e) => setTargetLanguage(e.target.value)}
                className="app-select mt-3"
              >
                <option value="">Mismo idioma</option>
                <option value="Spanish">Espanol</option>
                <option value="English">English</option>
                <option value="Portuguese">Portugues</option>
              </select>
            </div>
          </div>

          <div className="mt-3 flex flex-col gap-3 md:flex-row">
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

          {!immersiveMode && hasAssistantMessage ? (
            <div className="mt-6">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
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
          ) : null}
        </motion.div>
      </div>
    </motion.section>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={null}>
      <ChatPageContent />
    </Suspense>
  );
}
