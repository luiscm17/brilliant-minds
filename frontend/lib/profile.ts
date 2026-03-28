import { STORAGE_KEYS } from "./api";
import type {
  AccessibilityPreset,
  AdaptationIntensity,
  ConditionType,
  CognitivePriority,
  ExperienceDraft,
  PalettePreference,
  ReadingLevel,
  UserProfile,
} from "./types";

export const DEFAULT_EXPERIENCE_DRAFT: ExperienceDraft = {
  palettePreference: "neutral",
  condition: "manual",
  readingLevel: "A2",
  intensity: "balanced",
  maxSentenceLength: 10,
  tone: "calm_supportive",
  priorities: ["focus", "short_sentences"],
};

const EXPERIENCE_DRAFT_EVENT = "experience-draft-change";
let cachedDraftRaw: string | null = null;
let cachedDraftValue: ExperienceDraft = DEFAULT_EXPERIENCE_DRAFT;

export function deriveConditionFromPalette(
  palettePreference: PalettePreference,
): ConditionType {
  switch (palettePreference) {
    case "calm":
      return "adhd";
    case "contrast":
      return "dyslexia";
    case "harmony":
      return "combined";
    default:
      return "manual";
  }
}

function derivePaletteFromCondition(
  condition: ConditionType,
): PalettePreference {
  switch (condition) {
    case "adhd":
      return "calm";
    case "dyslexia":
      return "contrast";
    case "combined":
      return "harmony";
    default:
      return "neutral";
  }
}

function derivePreset(condition: ConditionType): AccessibilityPreset {
  if (condition === "combined") return "combined";
  if (condition === "dyslexia") return "dyslexia";
  if (condition === "adhd") return "adhd";
  return "custom";
}

export function getPaletteLabel(palettePreference: PalettePreference): string {
  switch (palettePreference) {
    case "calm":
      return "Arena + cielo";
    case "contrast":
      return "Marfil + azul";
    case "harmony":
      return "Salvia + niebla";
    default:
      return "Crema + grafito";
  }
}

export function getPaletteDescription(
  palettePreference: PalettePreference,
): string {
  switch (palettePreference) {
    case "calm":
      return "Beige suave, azul humo y verde salvia.";
    case "contrast":
      return "Marfil limpio, azul profundo y acento mandarina.";
    case "harmony":
      return "Salvia suave, niebla clara y azul sereno.";
    default:
      return "Crema clara, grafito suave y acentos naturales.";
  }
}

export function getPaletteSwatches(
  palettePreference: PalettePreference,
): string[] {
  switch (palettePreference) {
    case "calm":
      return ["#F5EEDC", "#A7C7E7", "#CFE1B9"];
    case "contrast":
      return ["#FFFFFF", "#004488", "#EE7733"];
    case "harmony":
      return ["#EAF0E3", "#BFD7EA", "#C1E1C1"];
    default:
      return ["#FBF7EF", "#1C1C1C", "#DFE8CF"];
  }
}

export function getPaletteColorLine(
  palettePreference: PalettePreference,
): string {
  switch (palettePreference) {
    case "calm":
      return "beige · cielo · salvia";
    case "contrast":
      return "marfil · azul · mandarina";
    case "harmony":
      return "salvia · niebla · cielo";
    default:
      return "crema · grafito · musgo";
  }
}

export function getPaletteThemeClass(
  palettePreference: PalettePreference,
): string {
  switch (palettePreference) {
    case "calm":
      return "theme-calm";
    case "contrast":
      return "theme-contrast";
    case "harmony":
      return "theme-harmony";
    default:
      return "theme-neutral";
  }
}

export function inferPaletteFromProfile(profile: UserProfile): PalettePreference {
  if (profile.preset === "combined") {
    return "harmony";
  }
  if (profile.preset === "dyslexia" || profile.priorities.includes("contrast")) {
    return "contrast";
  }
  if (profile.preset === "adhd" || profile.priorities.includes("focus")) {
    return "calm";
  }
  return "neutral";
}

export function createDraftFromPalette(
  palettePreference: PalettePreference,
): ExperienceDraft {
  const condition = deriveConditionFromPalette(palettePreference);
  const base = {
    ...DEFAULT_EXPERIENCE_DRAFT,
    palettePreference,
    condition,
  };

  switch (palettePreference) {
    case "calm":
      return {
        ...base,
        readingLevel: "A2",
        intensity: "balanced",
        maxSentenceLength: 10,
        tone: "neutral_clear",
        priorities: ["focus", "step_by_step", "short_sentences"],
      };
    case "contrast":
      return {
        ...base,
        readingLevel: "A1",
        intensity: "balanced",
        maxSentenceLength: 8,
        tone: "calm_supportive",
        priorities: ["contrast", "short_sentences", "calm"],
      };
    case "harmony":
      return {
        ...base,
        readingLevel: "A1",
        intensity: "strong",
        maxSentenceLength: 8,
        tone: "calm_supportive",
        priorities: ["focus", "contrast", "short_sentences", "step_by_step"],
      };
    default:
      return base;
  }
}

export function createDraftFromCondition(
  condition: ConditionType,
): ExperienceDraft {
  const palettePreference = derivePaletteFromCondition(condition);
  const base = { ...DEFAULT_EXPERIENCE_DRAFT, palettePreference, condition };

  switch (condition) {
    case "adhd":
      return createDraftFromPalette("calm");
    case "dyslexia":
      return createDraftFromPalette("contrast");
    case "combined":
      return createDraftFromPalette("harmony");
    case "unsure":
      return {
        ...base,
        readingLevel: "A2",
        intensity: "light",
        maxSentenceLength: 12,
        tone: "calm_supportive",
        priorities: ["focus", "calm"],
      };
    default:
      return base;
  }
}

export function applyIntensityToDraft(
  draft: ExperienceDraft,
  intensity: AdaptationIntensity,
): ExperienceDraft {
  const intensityMap: Record<
    AdaptationIntensity,
    { maxSentenceLength: number; readingLevel: ReadingLevel }
  > = {
    light: { maxSentenceLength: 14, readingLevel: "B1" },
    balanced: { maxSentenceLength: 10, readingLevel: "A2" },
    strong: { maxSentenceLength: 8, readingLevel: "A1" },
  };

  const target = intensityMap[intensity];

  return {
    ...draft,
    intensity,
    maxSentenceLength: target.maxSentenceLength,
    readingLevel: target.readingLevel,
  };
}

export function createProfileFromDraft(draft: ExperienceDraft): UserProfile {
  const resolvedCondition = draft.palettePreference
    ? deriveConditionFromPalette(draft.palettePreference)
    : draft.condition;

  return {
    hasAdhd: resolvedCondition === "adhd" || resolvedCondition === "combined",
    hasDyslexia:
      resolvedCondition === "dyslexia" || resolvedCondition === "combined",
    readingLevel: draft.readingLevel,
    preset: derivePreset(resolvedCondition),
    maxSentenceLength: draft.maxSentenceLength,
    tone: draft.tone,
    priorities: draft.priorities,
  };
}

export function sanitizeDraft(value: unknown): ExperienceDraft {
  const candidate = value as Partial<ExperienceDraft> | null;

  if (!candidate) {
    return DEFAULT_EXPERIENCE_DRAFT;
  }

  return {
    palettePreference:
      candidate.palettePreference ??
      derivePaletteFromCondition(
        candidate.condition ?? DEFAULT_EXPERIENCE_DRAFT.condition,
      ),
    condition: candidate.condition ?? DEFAULT_EXPERIENCE_DRAFT.condition,
    readingLevel: candidate.readingLevel ?? DEFAULT_EXPERIENCE_DRAFT.readingLevel,
    intensity: candidate.intensity ?? DEFAULT_EXPERIENCE_DRAFT.intensity,
    maxSentenceLength:
      candidate.maxSentenceLength ?? DEFAULT_EXPERIENCE_DRAFT.maxSentenceLength,
    tone: candidate.tone ?? DEFAULT_EXPERIENCE_DRAFT.tone,
    priorities: Array.isArray(candidate.priorities)
      ? (candidate.priorities as CognitivePriority[])
      : DEFAULT_EXPERIENCE_DRAFT.priorities,
  };
}

export function readExperienceDraft(): ExperienceDraft {
  if (typeof window === "undefined") {
    return DEFAULT_EXPERIENCE_DRAFT;
  }

  const rawValue = window.localStorage.getItem(STORAGE_KEYS.experienceDraft);

  if (!rawValue) {
    cachedDraftRaw = null;
    cachedDraftValue = DEFAULT_EXPERIENCE_DRAFT;
    return DEFAULT_EXPERIENCE_DRAFT;
  }

  if (rawValue === cachedDraftRaw) {
    return cachedDraftValue;
  }

  try {
    cachedDraftRaw = rawValue;
    cachedDraftValue = sanitizeDraft(JSON.parse(rawValue));
    return cachedDraftValue;
  } catch {
    cachedDraftRaw = null;
    cachedDraftValue = DEFAULT_EXPERIENCE_DRAFT;
    return DEFAULT_EXPERIENCE_DRAFT;
  }
}

export function writeExperienceDraft(draft: ExperienceDraft) {
  if (typeof window === "undefined") {
    return;
  }

  const serializedDraft = JSON.stringify(draft);
  cachedDraftRaw = serializedDraft;
  cachedDraftValue = draft;
  window.localStorage.setItem(STORAGE_KEYS.experienceDraft, serializedDraft);
  window.dispatchEvent(new Event(EXPERIENCE_DRAFT_EVENT));
}

export function subscribeExperienceDraft(callback: () => void) {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  const handler = () => callback();
  window.addEventListener("storage", handler);
  window.addEventListener(EXPERIENCE_DRAFT_EVENT, handler);

  return () => {
    window.removeEventListener("storage", handler);
    window.removeEventListener(EXPERIENCE_DRAFT_EVENT, handler);
  };
}
