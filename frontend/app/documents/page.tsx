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

export default function Documents() {
  const router = useRouter();
  const { isAuthenticated, profile } = useUser();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<DocumentUploadResult | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
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
    async function loadDocuments() {
      try {
        const nextDocuments = await listDocuments();
        setDocuments(nextDocuments);
      } catch {
        setError("No fue posible cargar tus documentos.");
      } finally {
        setLoadingDocuments(false);
      }
    }

    if (isAuthenticated && profile) {
      void loadDocuments();
    }
  }, [isAuthenticated, profile]);

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

  const handleDelete = async (documentId: string) => {
    try {
      await deleteDocument(documentId);
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
      className="studio-panel w-full p-6 md:p-8"
    >
      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <motion.div
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.08, duration: 0.4 }}
          className="rounded-[28px] bg-[rgba(255,255,255,0.62)] p-6 md:p-7"
        >
          <span className="eyebrow">Document intake</span>
          <h1 className="display-title mt-5 text-5xl md:text-6xl">
            prepara
            <br />
            el contexto
          </h1>
          <p className="muted-copy mt-5 max-w-xl text-base leading-7">
            Sube un PDF o Word y deja listo el material para mostrar
            simplificacion, grounding y adaptacion a lectura accesible.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <div className="tone-card">
              <p className="text-sm font-semibold text-slate-800">Acepta</p>
              <p className="mt-2 text-sm text-slate-600">PDF, DOC y DOCX</p>
            </div>
            <div className="tone-card">
              <p className="text-sm font-semibold text-slate-800">Destino</p>
              <p className="mt-2 text-sm text-slate-600">Pipeline de documentos</p>
            </div>
            <div className="tone-card">
              <p className="text-sm font-semibold text-slate-800">Salida</p>
              <p className="mt-2 text-sm text-slate-600">Estado listo para chat</p>
            </div>
          </div>

          <div className="mt-8 rounded-[24px] bg-white/70 p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                Documentos cargados
              </p>
              <span className="status-pill">{documents.length} items</span>
            </div>

            <div className="mt-4 space-y-3">
              {loadingDocuments ? (
                <p className="text-sm text-slate-500">Cargando documentos...</p>
              ) : documents.length === 0 ? (
                <p className="text-sm leading-6 text-slate-500">
                  Aun no hay documentos. Cuando conectes backend, aqui debe
                  venir `GET /documents`.
                </p>
              ) : (
                documents.map((document) => (
                  <div
                    key={document.documentId}
                    className="flex items-center justify-between rounded-2xl border border-[rgba(23,49,59,0.08)] bg-white px-4 py-3"
                  >
                    <div>
                      <p className="font-semibold text-slate-800">
                        {document.filename}
                      </p>
                      <p className="text-sm text-slate-500">
                        Estado: {document.status}
                      </p>
                    </div>
                    <button
                      onClick={() => handleDelete(document.documentId)}
                      className="secondary-button px-4 py-2 text-sm"
                    >
                      Eliminar
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-8 rounded-[24px] bg-[rgba(255,250,242,0.78)] p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
              Pipeline de demo
            </p>
            <div className="mt-4">
              <PipelineTimeline
                steps={[
                  {
                    title: "Documento recibido",
                    description:
                      "El archivo entra al flujo de procesamiento.",
                    state: result ? "done" : "active",
                  },
                  {
                    title: "Extraccion y grounding",
                    description:
                      "Se prepara el contenido para consultas posteriores.",
                    state: result ? "active" : "idle",
                  },
                  {
                    title: "Listo para chat",
                    description:
                      "El agente podra responder usando el documento como contexto.",
                    state: result ? "idle" : "idle",
                  },
                ]}
              />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.14, duration: 0.4 }}
          className="rounded-[28px] bg-[linear-gradient(180deg,rgba(255,250,242,0.96),rgba(250,244,232,0.82))] p-6 md:p-7"
        >
          <div className="flex items-center justify-between">
            <span className="eyebrow">Carga</span>
            <span className="status-pill">Nivel {profile.readingLevel}</span>
          </div>

          <div className="mt-8 rounded-[24px] border border-dashed border-[rgba(13,122,116,0.24)] bg-[rgba(213,235,225,0.26)] p-5">
            <p className="text-lg font-semibold text-slate-800">
              Arrastra o selecciona un archivo
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Si vas a hacer una demo, usa un documento largo o denso para que
              el antes y despues sea mas evidente.
            </p>

            <input
              accept=".pdf,.doc,.docx"
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
            <div className="mt-4 rounded-2xl bg-white/80 p-4 text-sm text-slate-700">
              Archivo seleccionado: <span className="font-semibold">{file.name}</span>
            </div>
          ) : null}

          {error ? (
            <div className="mt-4 rounded-2xl bg-[rgba(222,123,89,0.14)] p-4 text-sm text-[#96472f]">
              {error}
            </div>
          ) : null}

          {result ? (
            <div className="mt-4 rounded-2xl bg-[rgba(13,122,116,0.12)] p-4 text-sm text-[var(--teal-deep)]">
              Documento {result.filename} enviado. Estado actual: {result.status}.
            </div>
          ) : null}

          <div className="mt-6">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
              Vista previa del valor
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
              onClick={() => router.push("/chat")}
              className="secondary-button"
            >
              Ir al chat
            </button>
          </div>
        </motion.div>
      </div>
    </motion.section>
  );
}
