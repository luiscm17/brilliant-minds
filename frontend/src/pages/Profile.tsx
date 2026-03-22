import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usersApi } from "../api/endpoints";
import { useAuthStore } from "../store/auth";
import ProgressChart from "../components/ProgressChart";

const PRESETS = [
  { id: "TDAH",      label: "TDAH",       desc: "Bullets cortos y timers", emoji: "⚡" },
  { id: "Dislexia",  label: "Dislexia",   desc: "Frases muy cortas, fuente OpenDyslexic", emoji: "📖" },
  { id: "Combinado", label: "Combinado",  desc: "Todo activado, máxima calma", emoji: "🌿" },
  { id: "Docente",   label: "Docente",    desc: "Múltiples niveles simultáneos", emoji: "🎓" },
];

const LEVELS = ["A1", "A2", "B1", "B2", "C1"];

export default function Profile() {
  const { profile, setProfile } = useAuthStore();
  const navigate = useNavigate();
  const [preset, setPreset] = useState<"Dislexia" | "TDAH" | "Combinado" | "Docente">(profile?.preset ?? "TDAH");
  const [level, setLevel] = useState(profile?.reading_level ?? "A2");
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      const res = await usersApi.updateMe({ preset: preset as any, reading_level: level as any });
      setProfile(res.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg pb-12">
      <header className="bg-surface border-b border-gray-200 px-6 py-4 flex items-center gap-4">
        <button onClick={() => navigate("/dashboard")} className="text-textSub hover:text-textMain text-xl">←</button>
        <h1 className="text-base font-semibold text-textMain">Mi perfil de accesibilidad</h1>
      </header>

      <main className="max-w-lg mx-auto px-4 py-8 space-y-6">
        {/* Preset */}
        <div className="card">
          <h2 className="font-semibold mb-1">¿Cómo lees mejor?</h2>
          <p className="text-textSub text-sm mb-4">El agente adapta el texto a tu estilo</p>
          <div className="grid grid-cols-2 gap-3">
            {PRESETS.map((p) => (
              <button
                key={p.id}
                onClick={() => setPreset(p.id as "Dislexia" | "TDAH" | "Combinado" | "Docente")}
                className={`p-4 rounded-xl border-2 text-left transition-all ${
                  preset === p.id
                    ? "border-primary bg-primary/5"
                    : "border-gray-200 bg-white hover:border-primary/40"
                }`}
              >
                <div className="text-2xl mb-1">{p.emoji}</div>
                <div className="font-semibold text-sm">{p.label}</div>
                <div className="text-xs text-textSub mt-0.5">{p.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Reading level */}
        <div className="card">
          <h2 className="font-semibold mb-1">Nivel de lectura</h2>
          <p className="text-textSub text-sm mb-4">A1 es el más simple, C1 conserva más detalle</p>
          <div className="flex gap-2">
            {LEVELS.map((l) => (
              <button
                key={l}
                onClick={() => setLevel(l)}
                className={`flex-1 py-2.5 rounded-xl font-semibold text-sm transition-all ${
                  level === l ? "bg-primary text-white" : "bg-white border border-gray-200 text-textSub hover:border-primary/40"
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        {/* Save */}
        <button onClick={handleSave} disabled={loading} className="btn-primary w-full">
          {saved ? "✅ Guardado" : loading ? "Guardando..." : "Guardar cambios"}
        </button>

        {/* Progress chart */}
        <ProgressChart history={profile?.fatigue_history ?? []} />
      </main>
    </div>
  );
}
