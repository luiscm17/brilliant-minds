import { useState } from "react";
import { usersApi } from "../api/endpoints";
import { useAuthStore } from "../store/auth";

const PRESETS = [
  { id: "TDAH",      emoji: "⚡", label: "TDAH",      desc: "Bullets cortos, timers de foco" },
  { id: "Dislexia",  emoji: "📖", label: "Dislexia",  desc: "Fuente OpenDyslexic, frases cortas" },
  { id: "Combinado", emoji: "🌿", label: "Combinado", desc: "Todo activado, máxima calma" },
  { id: "Docente",   emoji: "🎓", label: "Docente",   desc: "Genera versiones A1 / A2 / B1" },
];

const LEVELS = [
  { id: "A1", desc: "Muy simple" },
  { id: "A2", desc: "Simple" },
  { id: "B1", desc: "Intermedio" },
  { id: "B2", desc: "Avanzado" },
  { id: "C1", desc: "Experto" },
];

interface Props {
  onDone: () => void;
}

export default function OnboardingModal({ onDone }: Props) {
  const { setProfile } = useAuthStore();
  const [step, setStep] = useState(0);
  const [preset, setPreset] = useState("TDAH");
  const [level, setLevel] = useState("A2");
  const [saving, setSaving] = useState(false);

  const finish = async () => {
    setSaving(true);
    try {
      const res = await usersApi.updateMe({ preset: preset as any, reading_level: level as any });
      setProfile(res.data);
    } finally {
      setSaving(false);
      localStorage.setItem("onboarding_done", "true");
      onDone();
    }
  };

  return (
    <div style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.5)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
      <div style={{ backgroundColor: "#F8F7F4", borderRadius: "1.5rem", maxWidth: "480px", width: "100%", padding: "2rem", boxShadow: "0 20px 60px rgba(0,0,0,0.2)" }}>

        {/* Step indicator */}
        <div className="flex gap-2 mb-6">
          {[0, 1].map((s) => (
            <div
              key={s}
              className={`h-1.5 flex-1 rounded-full transition-all ${s <= step ? "bg-primary" : "bg-gray-200"}`}
            />
          ))}
        </div>

        {step === 0 && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-textMain">¡Bienvenido a DocSimplify! 👋</h2>
              <p className="text-textSub text-sm mt-1">Cuéntanos cómo lees mejor para personalizar tu experiencia.</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {PRESETS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPreset(p.id)}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${
                    preset === p.id ? "border-primary bg-primary/5" : "border-gray-200 bg-white hover:border-primary/40"
                  }`}
                >
                  <div className="text-2xl mb-1">{p.emoji}</div>
                  <div className="font-semibold text-sm">{p.label}</div>
                  <div className="text-xs text-textSub mt-0.5">{p.desc}</div>
                </button>
              ))}
            </div>
            <button onClick={() => setStep(1)} className="btn-primary w-full">
              Continuar →
            </button>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-textMain">¿Qué nivel de detalle prefieres?</h2>
              <p className="text-textSub text-sm mt-1">A1 es el más simple, C1 conserva más detalle técnico.</p>
            </div>
            <div className="space-y-2">
              {LEVELS.map((l) => (
                <button
                  key={l.id}
                  onClick={() => setLevel(l.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border-2 text-left transition-all ${
                    level === l.id ? "border-primary bg-primary/5" : "border-gray-200 bg-white hover:border-primary/40"
                  }`}
                >
                  <span className={`font-bold text-base w-8 ${level === l.id ? "text-primary" : "text-textSub"}`}>{l.id}</span>
                  <span className="text-sm text-textMain">{l.desc}</span>
                  {level === l.id && <span className="ml-auto text-primary">✓</span>}
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button onClick={() => setStep(0)} className="btn-secondary flex-1">
                ← Atrás
              </button>
              <button onClick={finish} disabled={saving} className="btn-primary flex-1">
                {saving ? "Guardando..." : "¡Empezar! 🚀"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
