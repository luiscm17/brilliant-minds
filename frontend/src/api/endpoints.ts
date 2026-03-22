import { api } from "./client";

// ── Auth ────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; name: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
};

// ── Users ───────────────────────────────────────────────────────────────────
export const usersApi = {
  getMe: () => api.get("/users/me"),
  updateMe: (data: Partial<UserProfileUpdate>) => api.patch("/users/me", data),
};

// ── Documents ───────────────────────────────────────────────────────────────
export const documentsApi = {
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/documents", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: () => api.get("/documents"),
  delete: (documentId: string) => api.delete(`/documents/${documentId}`),
};

// ── Chats ───────────────────────────────────────────────────────────────────
export const chatsApi = {
  list: () => api.get("/chats"),
  create: (title?: string) => api.post("/chats", { title }),
  sendMessage: (
    chatId: string,
    message: string,
    documentIds?: string[],
    fatigueLevel?: number,
    targetLanguage?: string,
  ) =>
    api.post(`/chats/${chatId}/messages`, {
      message,
      document_ids: documentIds,
      fatigue_level: fatigueLevel ?? 0,
      target_language: targetLanguage ?? null,
    }),
  getComprehension: (chatId: string, simplifiedText: string) =>
    api.post(`/chats/${chatId}/comprehension`, { simplified_text: simplifiedText }),
  updateTitle: (chatId: string, title: string) =>
    api.patch(`/chats/${chatId}`, { title }),
  deleteChat: (chatId: string) => api.delete(`/chats/${chatId}`),
  shareResult: (chatId: string, result: SimplifiedResponse) =>
    api.post(`/chats/${chatId}/share`, result),
  getConceptMap: (chatId: string, simplifiedText: string) =>
    api.post(`/chats/${chatId}/concept-map`, { simplified_text: simplifiedText }),
};

// ── Shared (public, no auth) ─────────────────────────────────────────────────
export const sharedApi = {
  get: (token: string) => api.get(`/shared/${token}`),
};

// ── Types ───────────────────────────────────────────────────────────────────
export interface UserProfileUpdate {
  reading_level: "A1" | "A2" | "B1" | "B2" | "C1";
  max_sentence_length: number;
  tone: "calm_supportive" | "neutral" | "encouraging";
  avoid_words: string[];
  preset: "Dislexia" | "TDAH" | "Combinado" | "Docente";
}

export interface SimplifiedResponse {
  original_message: string;
  simplified_text: string;
  explanation: string;
  wcag_report: { score: number; passed: boolean; issues: string[] };
  audio_url?: string;
  preset_used?: string;
  reading_level_used?: string;
  emoji_summary?: string;
  glossary?: { word: string; definition: string }[];
  concept_map?: { nodes: { id: string; label: string }[]; edges: { source: string; target: string }[] } | null;
  searches_performed?: string[];
}

export interface UserDocument {
  document_id: string;
  filename: string;
  status: string;
  uploaded_at: string;
}
