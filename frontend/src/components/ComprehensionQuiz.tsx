import { useState } from "react";
import { chatsApi } from "../api/endpoints";

interface Question {
  question: string;
  options: { A: string; B: string; C: string };
  answer: string;
}

interface Props {
  simplifiedText: string;
  chatId: string;
  onResimplify?: () => void;
}

type QuizState = "idle" | "loading" | "active" | "done";

export default function ComprehensionQuiz({ simplifiedText, chatId, onResimplify }: Props) {
  const [state, setState] = useState<QuizState>("idle");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState(false);

  const load = async () => {
    setState("loading");
    try {
      const res = await chatsApi.getComprehension(chatId, simplifiedText);
      setQuestions(res.data.questions ?? []);
      setState("active");
    } catch {
      setState("idle");
    }
  };

  const select = (i: number, opt: string) => {
    if (submitted) return;
    setAnswers((a) => ({ ...a, [i]: opt }));
  };

  const submit = () => setSubmitted(true);

  const score = questions.filter((q, i) => answers[i] === q.answer).length;
  const passed = submitted && score >= Math.ceil(questions.length * 2 / 3);
  const needsResimplify = submitted && !passed && onResimplify;

  if (state === "idle") {
    return (
      <button
        onClick={load}
        className="btn-secondary w-full text-sm flex items-center justify-center gap-2"
      >
        ✋ ¿Entendiste? Verifica tu comprensión
      </button>
    );
  }

  if (state === "loading") {
    return (
      <div className="card text-center py-6 text-textSub text-sm animate-pulse">
        Generando preguntas...
      </div>
    );
  }

  return (
    <div className="card space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-textMain">✋ Verificar comprensión</h3>
        {submitted && (
          <span className={`text-sm font-semibold px-3 py-1 rounded-full ${
            passed ? "bg-success/20 text-green-700" : "bg-warning/20 text-yellow-700"
          }`}>
            {score}/{questions.length} correctas
          </span>
        )}
      </div>

      {submitted && (
        <div className="space-y-2">
          <p className="text-sm text-textSub">
            {score === questions.length
              ? "¡Excelente! Entendiste todo el contenido 🌟"
              : passed
              ? "¡Muy bien! Captaste las ideas principales 👍"
              : "Parece que algunas partes no quedaron claras. ¿Quieres una versión aún más simple? 🌿"}
          </p>
          {needsResimplify && (
            <button
              onClick={onResimplify}
              className="w-full py-2.5 rounded-xl text-sm font-medium border-2 border-primary text-primary hover:bg-primary/5 transition-all flex items-center justify-center gap-2"
            >
              🔄 Simplificar aún más
            </button>
          )}
        </div>
      )}

      <div className="space-y-5">
        {questions.map((q, i) => (
          <div key={i}>
            <p className="text-sm font-medium text-textMain mb-2">
              {i + 1}. {q.question}
            </p>
            <div className="space-y-2">
              {(["A", "B", "C"] as const).map((opt) => {
                const selected = answers[i] === opt;
                const isCorrect = submitted && opt === q.answer;
                const isWrong = submitted && selected && opt !== q.answer;
                return (
                  <button
                    key={opt}
                    onClick={() => select(i, opt)}
                    className={`w-full text-left px-4 py-2.5 rounded-xl text-sm border transition-all ${
                      isCorrect
                        ? "border-success bg-success/10 text-green-700"
                        : isWrong
                        ? "border-warning bg-warning/10 text-yellow-700"
                        : selected
                        ? "border-primary bg-primary/5 text-primary"
                        : "border-gray-200 text-textSub hover:border-primary/30"
                    }`}
                  >
                    <span className="font-semibold mr-2">{opt}.</span>
                    {q.options[opt]}
                    {isCorrect && <span className="ml-2">✅</span>}
                    {isWrong && <span className="ml-2">💡</span>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {!submitted && Object.keys(answers).length === questions.length && (
        <button onClick={submit} className="btn-primary w-full">
          Ver resultados
        </button>
      )}

      {submitted && (
        <button
          onClick={() => { setState("idle"); setAnswers({}); setSubmitted(false); setQuestions([]); }}
          className="btn-secondary w-full text-sm"
        >
          Cerrar quiz
        </button>
      )}
    </div>
  );
}
