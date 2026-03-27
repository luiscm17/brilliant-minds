"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import BeforeAfterPreview from "../../components/BeforeAfterPreview";
import PipelineTimeline from "../../components/PipelineTimeline";
import { useRouter } from "next/navigation";
import {
  deleteDocument,
  listDocuments,
  uploadDocument,
} from "../../lib/api";
import type { DocumentItem, DocumentUploadResult } from "../../lib/types";
import { useUser } from "../../context/UserContext";
import { getPaletteLabel, readExperienceDraft } from "../../lib/profile";

export default function Documents() {
  const router = useRouter();
  const { isAuthenticated, profile } = useUser();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<DocumentUploadResult | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const paletteLabel = getPaletteLabel(readExperienceDraft().palettePreference);

  const loadDocuments = async (preserveLoadingState = false) => {
    if (!preserveLoadingState) {
      setLoadingDocuments(true);
    }

    try {
      const nextDocuments = await listDocuments();
      setDocuments(nextDocuments);
      setResult((currentResult) => {
        if (!currentResult) {
          return currentResult;
        }

        const refreshedDocument = nextDocuments.find(
          (document) => document.documentId === currentResult.documentId,
        );

        return refreshedDocument
          ? { ...currentResult, status: refreshedDocument.status }
          : currentResult;
      });
    } catch {
      setError("No fue posible cargar tus documentos.");
    } finally {
      setLoadingDocuments(false);
    }
  };

  const pipelineSteps = [
    {
      title: "Documento recibido",
      description: "El archivo entra al flujo de procesamiento.",
      state: result ? "done" : uploading ? "active" : "idle",
    },
    {
      title: "Extraccion y grounding",
      description: "Se prepara el contenido para consultas posteriores.",
      state:
        result?.status === "processing"
          ? "active"
          : result?.status === "completed"
            ? "done"
            : "idle",
    },
    {
      title: "Listo para chat",
      description: "El agente podra responder usando el documento como contexto.",
      state: result?.status === "completed" ? "done" : "idle",
    },
  ] as const;

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
    if (isAuthenticated && profile) {
      void loadDocuments();
    }
  }, [isAuthenticated, profile]);

  useEffect(() => {
    const hasProcessingDocuments =
      result?.status === "processing" ||
      documents.some((document) => document.status === "processing");

    if (!hasProcessingDocuments) {
      return;
    }

    const intervalId = window.setInterval(() => {
      void loadDocuments(true);
    }, 12000);

    return () => window.clearInterval(intervalId);
  }, [documents, result]);

  const handleUpload = async () => {
    if (!file) {
      setError("Selecciona un archivo antes de subirlo.");
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const uploadResult = await uploadDocument(file);
      setResult(uploadResult);
      setDocuments((currentDocuments) => [uploadResult, ...currentDocuments]);
    } catch {
      setError(
        "No fue posible subir el documento. Revisa la conexion o intenta de nuevo.",
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: string, blobName?: string) => {
    try {
      await deleteDocument(documentId, blobName);
      setDocuments((currentDocuments) =>
        currentDocuments.filter((document) => document.documentId !== documentId),
      );
    } catch {
      setError("No fue posible eliminar el documento.");
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
      className="studio-panel hero-grid w-full p-6 md:p-8"
    >
      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <motion.div
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.08, duration: 0.4 }}
          className="dark-studio-panel rounded-[28px] p-6 text-white md:p-7"
        >
          <span className="eyebrow">Document intake</span>
          <h1 className="display-title mt-5 text-5xl md:text-6xl">
            prepara
            <br />
            el contexto
          </h1>
          <p className="reading-copy mt-5 text-base leading-8 text-white/84">
            Sube un PDF o Word y deja listo el material para demostrar como la
            lectura mejora cuando el texto tiene contexto real.
          </p>

          <div className="mt-6 flex flex-wrap gap-2">
            <span className="status-pill border-white/10 bg-white/10 text-white">
              {paletteLabel}
            </span>
            <span className="status-pill border-white/10 bg-white/10 text-white">
              Ingesta lista para chat
            </span>
            <span className="status-pill border-white/10 bg-white/10 text-white">
              Frontend sin tocar backend
            </span>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="reading-card">
              <p className="text-sm font-semibold text-white">Acepta</p>
              <p className="mt-2 text-sm text-white/72">PDF, DOC, DOCX y TXT</p>
            </div>
            <div className="reading-card">
              <p className="text-sm font-semibold text-white">Salida</p>
              <p className="mt-2 text-sm text-white/72">Estado listo para chat</p>
            </div>
          </div>

          <div className="mt-8 rounded-[24px] border border-white/12 bg-white/8 p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/56">
                Documentos cargados
              </p>
              <span className="status-pill border-white/10 bg-white/10 text-white">
                {documents.length} items
              </span>
            </div>

            <div className="mt-4 space-y-3">
              {loadingDocuments ? (
                <div className="space-y-3">
                  {[0, 1, 2].map((item) => (
                    <div key={item} className="reading-card">
                      <div className="skeleton-block h-4 w-44" />
                      <div className="mt-3 skeleton-block h-3 w-24" />
                    </div>
                  ))}
                </div>
              ) : documents.length === 0 ? (
                <p className="text-sm leading-6 text-white/66">
                  Aun no hay documentos. Sube uno largo, tecnico o visual para
                  que el cambio se note mejor en la demo.
                </p>
              ) : (
                documents.map((document) => (
                  <div
                    key={document.documentId}
                    className="flex items-center justify-between gap-4 rounded-2xl border border-white/12 bg-white/7 px-4 py-3"
                  >
                    <div>
                      <p className="font-semibold text-white">
                        {document.filename}
                      </p>
                      <p className="text-sm text-white/66">
                        Estado: {document.status}
                      </p>
                    </div>
                    <button
                      onClick={() => handleDelete(document.documentId, document.blobName)}
                      className="secondary-button border-white/10 bg-white/10 px-4 py-2 text-sm text-white"
                    >
                      Eliminar
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-8 rounded-[24px] border border-white/12 bg-white/8 p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/56">
              Estado del procesamiento
            </p>
            <div className="mt-4">
              <PipelineTimeline steps={[...pipelineSteps]} />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.14, duration: 0.4 }}
          className="rounded-[28px] border border-white/12 bg-[rgba(13,19,28,0.86)] p-6 md:p-7"
        >
          <div className="flex items-center justify-between">
            <span className="eyebrow">Carga</span>
            <span className="status-pill">{paletteLabel} - Nivel {profile.readingLevel}</span>
          </div>

          <div className="mt-8 rounded-[24px] border border-dashed border-[rgba(76,226,244,0.3)] bg-[rgba(76,226,244,0.08)] p-5">
            <p className="text-lg font-semibold text-white">
              Arrastra o selecciona un archivo
            </p>
            <p className="reading-copy mt-2 text-sm leading-7 text-white/76">
              Para una demo mas fuerte, usa un documento largo, tecnico o con
              imagenes para que el cambio de tono, estructura y lectura se note mejor.
            </p>

            <input
              accept=".pdf,.doc,.docx,.txt"
              className="app-input mt-5"
              type="file"
              onChange={(e) => {
                setFile(e.target.files?.[0] ?? null);
                setError(null);
                setResult(null);
              }}
            />
          </div>

          {file ? (
            <div className="mt-4 rounded-2xl border border-white/12 bg-white/8 p-4 text-sm text-white/78">
              Archivo seleccionado: <span className="font-semibold">{file.name}</span>
            </div>
          ) : null}

          {error ? (
            <div className="mt-4 rounded-2xl border border-[rgba(255,125,108,0.22)] bg-[rgba(255,125,108,0.12)] p-4 text-sm text-[#ffd2cb]">
              {error}
            </div>
          ) : null}

          {result ? (
            <div className="mt-4 rounded-2xl border border-[rgba(76,226,244,0.2)] bg-[rgba(76,226,244,0.1)] p-4 text-sm text-white/84">
              Documento {result.filename} enviado. Estado actual: {result.status}.
            </div>
          ) : null}

          <div className="mt-6">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
              Asi se vera la lectura
            </p>
            <div className="mt-4">
              <BeforeAfterPreview
                preset={profile.preset}
                readingLevel={profile.readingLevel}
                maxSentenceLength={profile.maxSentenceLength}
              />
            </div>
          </div>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="primary-button flex-1"
            >
              {uploading ? "Subiendo..." : "Subir documento"}
            </button>

            <button
              onClick={() => router.push("/chat?demo=1")}
              className="secondary-button"
            >
              Abrir chat guiado
            </button>
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
}
