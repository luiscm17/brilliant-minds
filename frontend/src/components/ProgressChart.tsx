import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const LEVEL_NUM: Record<string, number> = { A1: 1, A2: 2, B1: 3, B2: 4, C1: 5 };
const NUM_LEVEL: Record<number, string> = { 1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1" };

interface Entry {
  date: string;
  level: string;
  preset: string;
}

interface Props {
  history: Entry[];
}

export default function ProgressChart({ history }: Props) {
  if (!history || history.length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-3xl mb-2">📈</p>
        <p className="text-textSub text-sm">Aquí verás tu progreso cuando uses el agente.</p>
      </div>
    );
  }

  const data = history.slice(-20).map((e) => ({
    date: new Date(e.date).toLocaleDateString("es-ES", { day: "numeric", month: "short" }),
    nivel: LEVEL_NUM[e.level] ?? 2,
    preset: e.preset,
    label: e.level,
  }));

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-textMain">📈 Tu progreso</h2>
        <span className="text-xs text-textSub">{history.length} sesiones</span>
      </div>
      <p className="text-xs text-textSub">Nivel de lectura usado en cada sesión</p>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#9ca3af" }} />
          <YAxis
            domain={[1, 5]}
            tickFormatter={(v) => NUM_LEVEL[v] ?? v}
            tick={{ fontSize: 11, fill: "#9ca3af" }}
          />
          <Tooltip
            formatter={(value) => [NUM_LEVEL[Number(value)] ?? String(value), "Nivel"]}
            contentStyle={{ borderRadius: "8px", border: "1px solid #e5e7eb", fontSize: 12 }}
          />
          <Line
            type="monotone"
            dataKey="nivel"
            stroke="#5B8DEF"
            strokeWidth={2}
            dot={{ fill: "#5B8DEF", r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="flex gap-2 flex-wrap">
        {["A1", "A2", "B1", "B2", "C1"].map((l) => {
          const count = history.filter((e) => e.level === l).length;
          return count > 0 ? (
            <span key={l} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
              {l}: {count}x
            </span>
          ) : null;
        })}
      </div>
    </div>
  );
}
