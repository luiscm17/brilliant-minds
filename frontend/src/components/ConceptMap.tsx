import { useState, useCallback } from "react";
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
} from "reactflow";
import "reactflow/dist/style.css";
import { chatsApi } from "../api/endpoints";

interface Props {
  simplifiedText: string;
  chatId: string;
}

type LoadState = "idle" | "loading" | "ready";

export default function ConceptMap({ simplifiedText, chatId }: Props) {
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const load = async () => {
    setLoadState("loading");
    try {
      const res = await chatsApi.getConceptMap(chatId, simplifiedText);
      const data = res.data as { nodes: { id: string; label: string }[]; edges: { source: string; target: string }[] };

      // Layout: first node center, others in a circle
      const cx = 300, cy = 200, r = 150;
      const rfNodes = data.nodes.map((n, i) => ({
        id: n.id,
        data: { label: n.label },
        position: i === 0
          ? { x: cx, y: cy }
          : {
              x: cx + r * Math.cos((2 * Math.PI * (i - 1)) / (data.nodes.length - 1)),
              y: cy + r * Math.sin((2 * Math.PI * (i - 1)) / (data.nodes.length - 1)),
            },
        style: i === 0
          ? { background: "#5B8DEF", color: "#fff", border: "none", borderRadius: "12px", fontWeight: 600, fontSize: 13, padding: "8px 12px" }
          : { background: "#fff", border: "2px solid #5B8DEF", borderRadius: "10px", fontSize: 12, padding: "6px 10px" },
      }));

      const rfEdges = data.edges.map((e, i) => ({
        id: `e-${i}`,
        source: e.source,
        target: e.target,
        style: { stroke: "#5B8DEF", strokeWidth: 2 },
        animated: false,
      }));

      setNodes(rfNodes);
      setEdges(rfEdges);
      setLoadState("ready");
    } catch {
      setLoadState("idle");
    }
  };

  if (loadState === "idle") {
    return (
      <button
        onClick={load}
        className="btn-secondary w-full text-sm flex items-center justify-center gap-2"
      >
        🗺️ Ver mapa conceptual
      </button>
    );
  }

  if (loadState === "loading") {
    return (
      <div className="card text-center py-6 text-textSub text-sm animate-pulse">
        Generando mapa conceptual...
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="font-semibold text-textMain mb-3">🗺️ Mapa conceptual</h3>
      <div style={{ height: 400, borderRadius: "12px", overflow: "hidden", border: "1px solid #e5e7eb" }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background color="#f1f5f9" gap={16} />
          <Controls />
        </ReactFlow>
      </div>
      <p className="text-xs text-textSub mt-2">Puedes mover los nodos para reorganizar el mapa</p>
    </div>
  );
}
