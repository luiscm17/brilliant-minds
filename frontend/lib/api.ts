import type {
  AuthResponse,
  AuthUser,
  ChatResponse,
  ComprehensionQuestion,
  ConceptMap,
  CreateChatResponse,
  DocumentItem,
  DocumentUploadResult,
  LoginRequest,
  RegisterRequest,
  SendMessageRequest,
  ShareResponse,
  UserProfileDto,
} from "./types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001/api/v1";
const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK_API !== "false";

export const STORAGE_KEYS = {
  token: "auth_token",
  authUser: "auth_user",
  profile: "profile",
  experienceDraft: "experience_draft",
  mockProfile: "mock_user_profile",
  mockDocuments: "mock_documents",
  activeChatId: "active_chat_id",
} as const;

type JsonBody = Record<string, unknown>;

async function requestJson<T>(
  path: string,
  init?: Omit<RequestInit, "body"> & { body?: JsonBody },
): Promise<T> {
  const headers = new Headers(init?.headers);
  const token = getStoredToken();

  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    body: init?.body ? JSON.stringify(init.body) : undefined,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function readStorage<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") {
    return fallback;
  }

  const rawValue = window.localStorage.getItem(key);

  if (!rawValue) {
    return fallback;
  }

  try {
    return JSON.parse(rawValue) as T;
  } catch {
    return fallback;
  }
}

function writeStorage<T>(key: string, value: T) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(key, JSON.stringify(value));
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(STORAGE_KEYS.token);
}

export function getStoredAuthUser(): AuthUser | null {
  return readStorage<AuthUser | null>(STORAGE_KEYS.authUser, null);
}

export function persistSession(auth: AuthResponse) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(STORAGE_KEYS.token, auth.token);
  writeStorage(STORAGE_KEYS.authUser, auth.user);
}

export function clearSession() {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEYS.token);
  window.localStorage.removeItem(STORAGE_KEYS.authUser);
  window.localStorage.removeItem(STORAGE_KEYS.profile);
  window.localStorage.removeItem(STORAGE_KEYS.activeChatId);
}

export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  if (USE_MOCK_API) {
    await wait(320);

    const mockAuth: AuthResponse = {
      token: `mock-token-${crypto.randomUUID()}`,
      userId: crypto.randomUUID(),
      user: {
        userId: crypto.randomUUID(),
        email: credentials.email,
        name: credentials.email.split("@")[0] || "demo",
      },
    };

    persistSession(mockAuth);
    return mockAuth;
  }

  const auth = await requestJson<AuthResponse>("/auth/login", {
    method: "POST",
    body: credentials,
  });
  persistSession(auth);
  return auth;
}

export async function register(
  payload: RegisterRequest,
): Promise<AuthResponse> {
  if (USE_MOCK_API) {
    await wait(360);

    const mockAuth: AuthResponse = {
      token: `mock-token-${crypto.randomUUID()}`,
      userId: crypto.randomUUID(),
      user: {
        userId: crypto.randomUUID(),
        email: payload.email,
        name: payload.name,
      },
    };

    persistSession(mockAuth);
    return mockAuth;
  }

  const auth = await requestJson<AuthResponse>("/auth/register", {
    method: "POST",
    body: payload,
  });
  persistSession(auth);
  return auth;
}

export async function getCurrentUser(): Promise<UserProfileDto | null> {
  if (USE_MOCK_API) {
    await wait(200);
    return readStorage<UserProfileDto | null>(STORAGE_KEYS.mockProfile, null);
  }

  try {
    return await requestJson<UserProfileDto>("/users/me", { method: "GET" });
  } catch {
    return readStorage<UserProfileDto | null>(STORAGE_KEYS.profile, null);
  }
}

export async function updateCurrentUser(
  profile: UserProfileDto,
): Promise<UserProfileDto> {
  if (USE_MOCK_API) {
    await wait(300);
    writeStorage(STORAGE_KEYS.mockProfile, profile);
    writeStorage(STORAGE_KEYS.profile, profile);
    return profile;
  }

  try {
    return await requestJson<UserProfileDto>("/users/me", {
      method: "PATCH",
      body: profile,
    });
  } catch {
    writeStorage(STORAGE_KEYS.profile, profile);
    return profile;
  }
}

export async function listDocuments(): Promise<DocumentItem[]> {
  if (USE_MOCK_API) {
    await wait(250);
    return readStorage<DocumentItem[]>(STORAGE_KEYS.mockDocuments, []);
  }

  return requestJson<DocumentItem[]>("/documents", { method: "GET" });
}

export async function uploadDocument(
  file: File,
): Promise<DocumentUploadResult> {
  if (USE_MOCK_API) {
    await wait(500);

    const nextDocument: DocumentUploadResult = {
      success: true,
      documentId: crypto.randomUUID(),
      filename: file.name,
      status: "processing",
    };

    const currentDocuments = readStorage<DocumentItem[]>(
      STORAGE_KEYS.mockDocuments,
      [],
    );
    writeStorage(STORAGE_KEYS.mockDocuments, [nextDocument, ...currentDocuments]);

    return nextDocument;
  }

  const formData = new FormData();
  formData.append("file", file);

  const headers = new Headers();
  const token = getStoredToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}/documents`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed with status ${response.status}`);
  }

  return (await response.json()) as DocumentUploadResult;
}

export async function deleteDocument(
  documentId: string,
  blobName?: string,
): Promise<void> {
  if (USE_MOCK_API) {
    await wait(220);

    const currentDocuments = readStorage<DocumentItem[]>(
      STORAGE_KEYS.mockDocuments,
      [],
    );
    const nextDocuments = currentDocuments.filter(
      (document) => document.documentId !== documentId,
    );

    writeStorage(STORAGE_KEYS.mockDocuments, nextDocuments);
    return;
  }

  await requestJson<{ status: string }>(
    `/documents/${encodeURIComponent(blobName ?? documentId)}`,
    {
    method: "DELETE",
    },
  );
}

export async function createChat(title?: string): Promise<CreateChatResponse> {
  if (USE_MOCK_API) {
    await wait(220);
    return { chatId: crypto.randomUUID() };
  }

  return requestJson<CreateChatResponse>("/chats", {
    method: "POST",
    body: title ? { title } : {},
  });
}

export async function sendChatMessage(
  chatId: string,
  payload: SendMessageRequest,
): Promise<ChatResponse> {
  if (USE_MOCK_API) {
    await wait(700);

    const documentCount = payload.documentIds?.length ?? 0;
    const documentContext =
      documentCount > 0
        ? ` Se considero contexto de ${documentCount} documento(s).`
        : "";

    return {
      originalMessage: payload.message,
      simplifiedText: `Chat ${chatId.slice(0, 8)}: ${payload.message}`,
      explanation:
        "Se reorganizo el contenido en lenguaje mas directo y con tono calmado." +
        documentContext,
      tone: "calmado",
      audioUrl: null,
      beeLineOverlay: true,
      wcagReport: "WCAG draft ready",
      presetUsed: "custom",
      readingLevelUsed: payload.fatigueLevel && payload.fatigueLevel > 0 ? "A1" : "A2",
      emojiSummary: "🧠📄✨✅",
      glossary: [
        { word: "grounding", definition: "usar documentos reales como apoyo" },
      ],
      searchesPerformed: documentCount > 0 ? [payload.message] : [],
      visualReferences:
        documentCount > 0
          ? [
              {
                title: "Documento seleccionado",
                pageNumber: 1,
                path: "mock://selected-document",
                imageCaption: "Referencia visual simulada para la demo.",
                previewText: "Referencia visual simulada para la demo.",
                sourceKind: "image",
                sectionKind: "figure",
                kind: "layout_image",
              },
            ]
          : [],
    };
  }

  return requestJson<ChatResponse>(`/chats/${chatId}/messages`, {
    method: "POST",
    body: payload,
  });
}

export async function sendAgentMessage(
  payload: SendMessageRequest,
): Promise<ChatResponse> {
  if (USE_MOCK_API) {
    await wait(650);

    return {
      originalMessage: payload.message,
      simplifiedText: `Agente: ${payload.message}`,
      explanation:
        "Respuesta generada por el endpoint del agente para la demo.",
      tone: "empatico",
      audioUrl: null,
      beeLineOverlay: true,
      wcagReport: "Draft ready",
      presetUsed: "agent",
      readingLevelUsed: payload.fatigueLevel && payload.fatigueLevel > 0 ? "A1" : "A2",
      emojiSummary: "agente conectado",
      glossary: [],
      searchesPerformed: [],
      visualReferences: [],
    };
  }

  return requestJson<ChatResponse>("/chats/agent", {
    method: "POST",
    body: payload,
  });
}

export async function getChatComprehension(
  chatId: string,
  simplifiedText: string,
): Promise<{ questions: ComprehensionQuestion[] }> {
  if (USE_MOCK_API) {
    await wait(260);
    return {
      questions: [
        {
          question: "Cual es la idea principal del texto?",
          options: {
            A: "La primera idea clave",
            B: "Un detalle menor",
            C: "Algo no mencionado",
          },
          answer: "A",
        },
      ],
    };
  }

  return requestJson<{ questions: ComprehensionQuestion[] }>(
    `/chats/${chatId}/comprehension`,
    {
      method: "POST",
      body: { simplified_text: simplifiedText },
    },
  );
}

export async function getConceptMap(
  chatId: string,
  simplifiedText: string,
): Promise<ConceptMap> {
  if (USE_MOCK_API) {
    await wait(260);
    return {
      nodes: [
        { id: "1", label: "Tema central" },
        { id: "2", label: "Paso 1" },
        { id: "3", label: "Paso 2" },
      ],
      edges: [
        { source: "1", target: "2" },
        { source: "1", target: "3" },
      ],
    };
  }

  return requestJson<ConceptMap>(`/chats/${chatId}/concept-map`, {
    method: "POST",
    body: { simplified_text: simplifiedText },
  });
}

export async function shareChatResult(
  chatId: string,
  result: ChatResponse,
): Promise<ShareResponse> {
  if (USE_MOCK_API) {
    await wait(200);
    return {
      shareToken: crypto.randomUUID(),
      shareUrl: `${window.location.origin}/shared/mock-${chatId}`,
    };
  }

  return requestJson<ShareResponse>(`/chats/${chatId}/share`, {
    method: "POST",
    body: {
      originalMessage: result.originalMessage,
      simplifiedText: result.simplifiedText,
      explanation: result.explanation,
      tone: result.tone,
      audioUrl: result.audioUrl,
      beeLineOverlay: result.beeLineOverlay,
      wcagReport: result.wcagReport,
      presetUsed: result.presetUsed,
      readingLevelUsed: result.readingLevelUsed,
      emojiSummary: result.emojiSummary,
      glossary: result.glossary,
      searchesPerformed: result.searchesPerformed,
      visualReferences: result.visualReferences,
    },
  });
}
