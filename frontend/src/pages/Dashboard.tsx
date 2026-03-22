import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { documentsApi, chatsApi } from "../api/endpoints";
import type { UserDocument } from "../api/endpoints";
import { useAuthStore } from "../store/auth";
import { usersApi } from "../api/endpoints";
import AccessibilityBar from "../components/AccessibilityBar";
import { useChatStore } from "../store/chat";
import OnboardingModal from "../components/OnboardingModal";

export default function Dashboard() {
  const [documents, setDocuments] = useState<UserDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const { setProfile, profile, logout } = useAuthStore();
  const { chats, setChats } = useChatStore();
  const navigate = useNavigate();

  useEffect(() => {
    usersApi.getMe().then((res) => setProfile(res.data)).catch(() => {});
    documentsApi.list().then((res) => setDocuments(res.data.documents)).finally(() => setLoading(false));
    chatsApi.list().then((res) => setChats(res.data)).catch(() => {});
    if (!localStorage.getItem("onboarding_done")) {
      setShowOnboarding(true);
    }
  }, []);

  const handleFile = async (file: File) => {
    const allowed = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
    if (!allowed.includes(file.type)) return alert("Solo se admiten PDF, Word o texto.");
    setUploading(true);
    try {
      await documentsApi.upload(file);
      const res = await documentsApi.list();
      setDocuments(res.data.documents);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    await documentsApi.delete(id);
    setDocuments((d) => d.filter((doc) => doc.document_id !== id));
  };

  return (
    <div className="min-h-screen bg-bg flex flex-col">
      {showOnboarding && <OnboardingModal onDone={() => setShowOnboarding(false)} />}
      {/* Header */}
      <header className="bg-surface border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📄</span>
          <span className="font-semibold text-textMain text-lg">DocSimplify</span>
        </div>
        <div className="flex items-center gap-4">
          {profile && (
            <span className="text-textSub text-sm hidden sm:block">
              Hola, <span className="text-textMain font-medium">{profile.name}</span>
            </span>
          )}
          <button onClick={() => navigate("/profile")} className="btn-secondary py-2 px-4 text-sm">
            Mi perfil
          </button>
          <button onClick={logout} className="text-textSub text-sm hover:text-textMain">
            Salir
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-8">
        {/* Upload zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer mb-8 ${
            dragOver ? "border-primary bg-primary/5" : "border-gray-300 bg-surface hover:border-primary/50"
          }`}
          onClick={() => document.getElementById("file-input")?.click()}
        >
          <input id="file-input" type="file" className="hidden"
            accept=".pdf,.docx,.txt" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
          <div className="text-4xl mb-3">{uploading ? "⏳" : "📎"}</div>
          <p className="font-medium text-textMain">
            {uploading ? "Procesando tu documento..." : "Arrastra tu documento aquí"}
          </p>
          <p className="text-textSub text-sm mt-1">PDF, Word o texto · El agente lo simplificará</p>
          {!uploading && (
            <button className="btn-primary mt-4 text-sm px-4 py-2" onClick={(e) => { e.stopPropagation(); document.getElementById("file-input")?.click(); }}>
              Elegir archivo
            </button>
          )}
        </div>

        {/* Recent chats */}
        {chats.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-3">Chats recientes</h2>
            <ul className="space-y-2">
              {chats.slice(0, 5).map((chat: any) => (
                <li key={chat.chat_id}>
                  <button
                    onClick={() => navigate(`/chat/${chat.chat_id}`)}
                    className="w-full card py-3 flex items-center gap-3 hover:border hover:border-primary/30 transition-all text-left"
                  >
                    <span className="text-xl">💬</span>
                    <div className="min-w-0">
                      <p className="font-medium text-sm text-textMain truncate">{chat.title}</p>
                      <p className="text-xs text-textSub mt-0.5">
                        {new Date(chat.created_at).toLocaleDateString("es-ES", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                    <span className="ml-auto text-textSub text-sm">→</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Documents list */}
        <h2 className="text-lg font-semibold mb-4">Tus documentos</h2>
        {loading ? (
          <p className="text-textSub text-center py-8">Cargando...</p>
        ) : documents.length === 0 ? (
          <div className="card text-center py-10">
            <div className="text-3xl mb-2">📭</div>
            <p className="text-textSub">Aún no tienes documentos. ¡Sube uno para empezar!</p>
          </div>
        ) : (
          <ul className="space-y-3">
            {documents.map((doc) => (
              <li key={doc.document_id} className="card flex items-center justify-between gap-4 py-4">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-2xl flex-shrink-0">
                    {doc.filename.endsWith(".pdf") ? "📕" : doc.filename.endsWith(".docx") ? "📘" : "📄"}
                  </span>
                  <div className="min-w-0">
                    <p className="font-medium text-textMain truncate">{doc.filename}</p>
                    <p className="text-xs text-textSub mt-0.5">
                      {new Date(doc.uploaded_at).toLocaleDateString("es-ES", { day: "numeric", month: "short" })}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => navigate(`/chat/new?doc=${doc.document_id}&title=${encodeURIComponent(doc.filename)}`)}
                    className="btn-primary text-sm py-2 px-3"
                  >
                    Simplificar
                  </button>
                  <button
                    onClick={() => handleDelete(doc.document_id)}
                    className="text-textSub hover:text-red-400 transition-colors p-2"
                    title="Eliminar"
                  >
                    🗑️
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>

      <AccessibilityBar />
    </div>
  );
}

