"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useUser } from "../../context/UserContext";
import { getPaletteLabel, readExperienceDraft } from "../../lib/profile";

export default function Dashboard() {
  const router = useRouter();
  const { isAuthenticated, profile } = useUser();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    if (!profile) {
      router.replace("/onboarding");
    }
  }, [isAuthenticated, profile, router]);

  if (!isAuthenticated || !profile) {
    return null;
  }

  const paletteLabel = getPaletteLabel(readExperienceDraft().palettePreference);

  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="w-full space-y-6"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.985 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.05, duration: 0.45 }}
        className="studio-panel hero-grid overflow-hidden p-6 md:p-8"
      >
        <div className="orb right-[-3rem] top-[-2rem] h-36 w-36 bg-[rgba(0,68,136,0.18)]" />
        <div className="orb bottom-[-2rem] left-12 h-28 w-28 bg-[rgba(238,119,51,0.22)]" />
        <div className="challenge-ribbon right-[-4rem] top-[7rem] w-[18rem] rotate-[12deg]" />

        <div className="relative z-10 grid gap-7 xl:grid-cols-[1.1fr_0.9fr] xl:items-end">
          <div>
            <span className="eyebrow">Focus mode</span>
            <h1 className="display-title mt-5 max-w-4xl text-[3.6rem] leading-[0.93] md:text-[4.8rem]">
              leer ya no se siente
              <br />
              como cargar todo
              <br />
              al mismo tiempo
            </h1>
            <p className="reading-copy mt-5 text-base leading-8 md:text-lg">
              Tu espacio ya esta adaptado para reducir carga cognitiva, suavizar
              explicaciones y mantener un ritmo de lectura mas facil de seguir.
            </p>

            <div className="mt-6 flex flex-wrap gap-2">
              <span className="status-pill">Nivel {profile.readingLevel}</span>
              <span className="status-pill">{paletteLabel}</span>
              <span className="status-pill">
                Tono {profile.tone === "calm_supportive" ? "calmado" : "neutral"}
              </span>
              <span className="status-pill">Demo lista</span>
            </div>
          </div>

          <div className="dark-studio-panel rounded-[28px] p-5 text-white">
            <p className="text-sm uppercase tracking-[0.14em] text-white/60">
              Estilo visual activo
            </p>
            <p className="mt-3 text-3xl font-semibold text-white">
              {paletteLabel}
            </p>
            <p className="mt-3 text-sm leading-7 text-white/80">
              El sistema ya esta listo para procesar documentos, simplificar
              texto y responder desde el chat con el tono que configuraste.
            </p>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/56">
                  Tono
                </p>
                <p className="mt-2 font-semibold text-white">
                  {profile.tone === "calm_supportive"
                    ? "Calmado y contenedor"
                    : "Neutro y directo"}
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/56">
                  Frases
                </p>
                <p className="mt-2 font-semibold text-white">
                  Hasta {profile.maxSentenceLength} palabras
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <motion.button
          initial={{ opacity: 0, x: -18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.12, duration: 0.4 }}
          onClick={() => router.push("/documents")}
          className="studio-panel group hero-grid p-6 text-left md:p-7"
        >
          <span className="eyebrow">Paso 1</span>
          <h2 className="mt-5 text-4xl font-semibold text-white">
            Sube el material
          </h2>
          <p className="reading-copy mt-3 text-base leading-8">
            Carga un PDF o Word para preparar el contexto. Mientras mas denso
            sea el documento, mas evidente sera la mejora en la demo.
          </p>

          <div className="mt-7 grid gap-3 sm:grid-cols-2">
            <div className="reading-card">
              <p className="reading-label">
                Entrada
              </p>
              <p className="mt-2 text-sm leading-7 text-white/74">
                PDF, DOC y DOCX con texto complejo o muy extenso.
              </p>
            </div>
            <div className="reading-card">
              <p className="reading-label">
                Resultado
              </p>
              <p className="mt-2 text-sm leading-7 text-white/74">
                Documento listo para grounding y simplificacion.
              </p>
            </div>
          </div>

          <div className="mt-8 inline-flex rounded-full bg-[rgba(213,235,225,0.86)] px-5 py-3 text-base font-semibold text-[var(--teal-deep)] transition group-hover:bg-[rgba(213,235,225,1)]">
            Ir a documentos
          </div>
        </motion.button>

        <motion.button
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.18, duration: 0.4 }}
          onClick={() => router.push("/chat")}
          className="studio-panel dark-studio-panel group hero-grid overflow-hidden p-6 text-left text-white md:p-7"
        >
          <div className="relative z-10">
            <span className="eyebrow border-white/18 bg-white/10 text-white">
              Paso 2
            </span>
            <h2 className="mt-5 text-4xl font-semibold text-white">
              Conversa con el agente
            </h2>
            <p className="mt-3 max-w-2xl text-base leading-8 text-white/84">
              Pide versiones mas claras, bullets por prioridad cognitiva y
              explicaciones calmadas para demostrar el valor del challenge.
            </p>

            <div className="mt-7 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/65">
                  Pregunta ejemplo
                </p>
                <p className="mt-2 text-sm leading-6 text-white/88">
                  Simplifica este contrato en A2 y marca los puntos urgentes.
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/65">
                  Salida esperada
                </p>
                <p className="mt-2 text-sm leading-6 text-white/88">
                  Texto claro, explicacion calmada y estructura facil de leer.
                </p>
              </div>
            </div>

            <div className="mt-8 inline-flex rounded-full bg-white/16 px-5 py-3 text-base font-semibold text-white transition group-hover:bg-white/22">
              Abrir chat IA
            </div>
          </div>
        </motion.button>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.22, duration: 0.35 }}
        className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]"
      >
        <div className="studio-panel hero-grid p-5 md:p-6">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
            Prioridades activas
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            {profile.priorities.map((priority) => (
              <span key={priority} className="status-pill bg-white/85">
                {priority}
              </span>
            ))}
          </div>
          <p className="muted-copy mt-4 max-w-2xl text-sm leading-7">
            Estas prioridades ayudan a que la demo se vea coherente con la
            paleta elegida y con el tipo de apoyo cognitivo que espera el
            usuario.
          </p>
        </div>
        <div className="studio-panel hero-grid p-5 md:p-6">
          <p className="text-sm font-semibold uppercase tracking-[0.14em] text-white/60">
            Siguiente mejor paso
          </p>
          <p className="mt-4 text-2xl font-semibold text-white">
            Empieza por documentos si quieres una demo mas fuerte.
          </p>
          <p className="muted-copy mt-3 text-sm leading-7">
            Un archivo denso hace que la mejora se vea con mas claridad en el
            chat y en el comparador antes vs despues.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => router.push("/documents")}
              className="primary-button"
            >
              Cargar documento
            </button>
            <button
              onClick={() => router.push("/chat?demo=1")}
              className="secondary-button"
            >
              Lanzar demo guiada
            </button>
          </div>
        </div>
      </motion.div>
    </motion.section>
  );
}
