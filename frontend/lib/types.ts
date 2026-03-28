export type ReadingLevel = "A1" | "A2" | "B1" | "C1";

export type AccessibilityPreset =
  | "dyslexia"
  | "adhd"
  | "combined"
  | "custom";

export type PalettePreference =
  | "neutral"
  | "calm"
  | "contrast"
  | "harmony";

export type ConditionType =
  | "adhd"
  | "dyslexia"
  | "combined"
  | "manual"
  | "unsure";

export type AdaptationIntensity = "light" | "balanced" | "strong";

export type CognitivePriority =
  | "focus"
  | "calm"
  | "contrast"
  | "short_sentences"
  | "step_by_step";

export type DocumentStatus =
  | "uploaded"
  | "processing"
  | "completed"
  | "error";

export type UserProfile = {
  hasAdhd: boolean;
  hasDyslexia: boolean;
  readingLevel: ReadingLevel;
  preset: AccessibilityPreset;
  maxSentenceLength: number;
  tone: "calm_supportive" | "neutral_clear";
  priorities: CognitivePriority[];
};

export type ExperienceDraft = {
  palettePreference: PalettePreference;
  condition: ConditionType;
  readingLevel: ReadingLevel;
  intensity: AdaptationIntensity;
  maxSentenceLength: number;
  tone: "calm_supportive" | "neutral_clear";
  priorities: CognitivePriority[];
};

export type UserProfileDto = UserProfile;

export type AuthUser = {
  userId: string;
  email: string;
  name: string;
};

export type AuthResponse = {
  token: string;
  userId: string;
  user: AuthUser;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type RegisterRequest = {
  email: string;
  password: string;
  name: string;
};

export type DocumentItem = {
  documentId: string;
  filename: string;
  blobName?: string;
  status: DocumentStatus;
};

export type DocumentUploadResult = DocumentItem & {
  success: boolean;
};

export type CreateChatResponse = {
  chatId: string;
};

export type SendMessageRequest = {
  message: string;
  documentIds?: string[];
  fatigueLevel?: number;
  targetLanguage?: string | null;
};

export type ChatResponse = {
  originalMessage?: string | null;
  simplifiedText: string;
  explanation: string;
  audioUrl?: string | null;
  beeLineOverlay?: boolean;
  wcagReport?: string | null;
  tone: string;
  presetUsed?: string | null;
  readingLevelUsed?: string | null;
  emojiSummary?: string | null;
  glossary?: Array<{ word: string; definition: string }>;
  searchesPerformed?: string[];
  visualReferences?: Array<{
    title?: string | null;
    pageNumber?: number | null;
    path?: string | null;
    imageUrl?: string | null;
    imageCaption?: string | null;
    previewText?: string | null;
    sourceKind?: string | null;
    sectionKind?: string | null;
    kind: string;
  }>;
};

export type ShareResponse = {
  shareToken: string;
  shareUrl: string;
};

export type ConceptMap = {
  nodes: Array<{ id: string; label: string }>;
  edges: Array<{ source: string; target: string }>;
};

export type ComprehensionQuestion = {
  question: string;
  options: Record<string, string>;
  answer: string;
};

export type ChatMessage =
  | {
      id: string;
      role: "user";
      text: string;
    }
  | {
      id: string;
      role: "assistant";
      data: ChatResponse;
    };
