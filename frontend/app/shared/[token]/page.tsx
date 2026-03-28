"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import ChatResultCard from "../../../components/ChatResultCard";
import type { ChatResponse } from "../../../lib/types";

export default function SharedPage() {
  const params = useParams<{ token: string }>();
  const [data, setData] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadShared() {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001/api/v1"}/shared/${params.token}`,
        );
        if (!response.ok) {
          throw new Error("not-found");
        }
        setData((await response.json()) as ChatResponse);
      } catch {
        setError("No fue posible cargar este resultado compartido.");
      }
    }

    if (params.token) {
      void loadShared();
    }
  }, [params.token]);

  if (error) {
    return (
      <div className="studio-panel hero-grid w-full p-6 text-sm text-[#96472f]">
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="studio-panel hero-grid w-full p-6 text-sm text-slate-500">
        Cargando...
      </div>
    );
  }

  return (
    <section className="studio-panel hero-grid w-full p-6 md:p-8">
      <span className="eyebrow">Resultado compartido</span>
      <h1 className="display-title mt-5 text-4xl md:text-5xl">lectura adaptada</h1>
      <p className="muted-copy mt-4 max-w-2xl text-base leading-7">
        Esta vista mantiene la misma logica visual del resto de la experiencia:
        claridad, foco y lectura mas facil de seguir.
      </p>
      <div className="mt-6 rounded-[24px] border border-[rgba(0,68,136,0.12)] bg-white/70 p-5">
        <ChatResultCard chatId={null} response={data} />
      </div>
    </section>
  );
}
