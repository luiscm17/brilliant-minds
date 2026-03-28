"use client";

type BrandMarkProps = {
  compact?: boolean;
  showTagline?: boolean;
  className?: string;
};

export default function BrandMark({
  compact = false,
  showTagline = false,
  className = "",
}: BrandMarkProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`.trim()}>
      <div
        className={`relative overflow-hidden rounded-[28px] border border-white/12 bg-[linear-gradient(180deg,rgba(57,212,238,0.2),rgba(57,212,238,0.06))] shadow-[0_18px_40px_rgba(35,209,233,0.18)] ${
          compact ? "h-12 w-12" : "h-16 w-16"
        }`}
      >
        <svg
          viewBox="0 0 128 128"
          className="h-full w-full"
          aria-hidden="true"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="brainFill" x1="14" y1="10" x2="114" y2="118">
              <stop offset="0%" stopColor="#4CE2F4" />
              <stop offset="100%" stopColor="#2AB1F1" />
            </linearGradient>
          </defs>
          <path
            d="M32 34C32 21 42 12 55 12C63 12 70 16 74 22C78 14 86 10 95 10C108 10 118 20 118 34C118 41 115 47 110 51C113 55 114 60 114 65C114 79 103 90 89 90H77V110C77 116 72 121 66 121C60 121 55 116 55 110V89H39C25 89 14 78 14 64C14 58 16 53 20 48C13 44 10 37 10 29C10 15 21 4 35 4C43 4 50 8 54 14"
            fill="url(#brainFill)"
          />
          <path
            d="M46 30V55M46 55L31 68M46 55L59 66M78 25V46M78 46L94 57M78 46L65 57M94 31V57M31 40V68M59 66V84M65 57V83M94 57V78"
            stroke="white"
            strokeWidth="6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="46" cy="30" r="6.5" fill="white" />
          <circle cx="46" cy="55" r="6.5" fill="white" />
          <circle cx="31" cy="68" r="6.5" fill="white" />
          <circle cx="59" cy="66" r="6.5" fill="white" />
          <circle cx="78" cy="25" r="6.5" fill="white" />
          <circle cx="78" cy="46" r="6.5" fill="white" />
          <circle cx="94" cy="57" r="6.5" fill="white" />
          <circle cx="65" cy="57" r="6.5" fill="white" />
          <circle cx="94" cy="31" r="6.5" fill="white" />
          <circle cx="31" cy="40" r="6.5" fill="white" />
          <circle cx="59" cy="84" r="6.5" fill="white" />
          <circle cx="65" cy="83" r="6.5" fill="white" />
          <circle cx="94" cy="78" r="6.5" fill="white" />
        </svg>
      </div>

      <div className="min-w-0">
        <p className="truncate text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent-cyan)]">
          DocSimplify AI
        </p>
        <p
          className={`truncate font-semibold text-[var(--ink)] ${
            compact ? "text-sm" : "text-lg"
          }`}
        >
          lectura clara, guiada y responsable
        </p>
        {showTagline ? (
          <p className="mt-1 max-w-md text-sm leading-6 text-[var(--muted)]">
            Ajusta la experiencia por preferencia visual, no por etiquetas
            clínicas visibles.
          </p>
        ) : null}
      </div>
    </div>
  );
}
