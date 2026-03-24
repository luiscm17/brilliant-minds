"use client";

import { useUser } from "../context/UserContext";
import type { UserProfile } from "../lib/types";
import { createProfileFromDraft, readExperienceDraft } from "../lib/profile";

export default function AccessibilityWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const { profile } = useUser();

  const sourceProfile = profile ?? createProfileFromDraft(readExperienceDraft());

  const safeProfile: UserProfile = {
    hasAdhd: sourceProfile.hasAdhd ?? false,
    hasDyslexia: sourceProfile.hasDyslexia ?? false,
    readingLevel: sourceProfile.readingLevel ?? "A1",
    preset: sourceProfile.preset ?? "custom",
    maxSentenceLength: sourceProfile.maxSentenceLength ?? 10,
    tone: sourceProfile.tone ?? "calm_supportive",
    priorities: Array.isArray(sourceProfile.priorities)
      ? sourceProfile.priorities
      : [],
  };

  const themeClass =
    safeProfile.preset === "combined"
      ? "theme-combined"
      : safeProfile.hasDyslexia
        ? "theme-dyslexia"
        : safeProfile.hasAdhd
          ? "theme-adhd"
          : "theme-default";

  const toneClass =
    safeProfile.tone === "calm_supportive" ? "tone-calm" : "tone-neutral";

  const densityClass =
    safeProfile.maxSentenceLength <= 8
      ? "density-compact"
      : safeProfile.maxSentenceLength <= 12
        ? "density-balanced"
        : "density-relaxed";

  const focusClass = safeProfile.priorities.includes("focus")
    ? "focus-emphasis"
    : "";

  const contrastClass = safeProfile.priorities.includes("contrast")
    ? "contrast-emphasis"
    : "";

  return (
    <div
      className={`theme-root ${themeClass} ${toneClass} ${densityClass} ${focusClass} ${contrastClass} min-h-screen transition-all duration-300`}
    >
      {children}
    </div>
  );
}
