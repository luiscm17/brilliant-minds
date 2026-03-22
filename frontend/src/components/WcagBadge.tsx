interface Props {
  report: { score: number; passed: boolean; issues: string[] };
}

export default function WcagBadge({ report }: Props) {
  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm
      ${report.passed ? "bg-success/10 text-green-700" : "bg-warning/10 text-yellow-700"}`}>
      <span className="text-xl">{report.passed ? "✅" : "💡"}</span>
      <div>
        <span className="font-semibold">Accesibilidad: {report.score}/100</span>
        {report.issues.length > 0 && (
          <p className="text-xs opacity-80 mt-0.5">
            {report.passed ? "Todo en orden" : `Oportunidad de mejora: ${report.issues[0]}`}
          </p>
        )}
      </div>
    </div>
  );
}
