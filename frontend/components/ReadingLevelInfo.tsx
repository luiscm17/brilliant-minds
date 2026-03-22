import type { ReadingLevel } from "../lib/types";

const readingLevelCopy: Record<ReadingLevel, string> = {
  A1: "Texto muy simple, frases cortas.",
  A2: "Texto claro con vocabulario comun.",
  B1: "Texto intermedio con algo de detalle.",
  C1: "Texto avanzado y tecnico.",
};

export default function ReadingLevelInfo({ level }: { level: ReadingLevel }) {
  return <p className="text-sm text-gray-500">{readingLevelCopy[level]}</p>;
}
