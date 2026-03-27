"use client";

type PipelineStep = {
  title: string;
  description: string;
  state: "idle" | "active" | "done";
};

type PipelineTimelineProps = {
  steps: PipelineStep[];
};

export default function PipelineTimeline({ steps }: PipelineTimelineProps) {
  return (
    <div className="space-y-3">
      {steps.map((step, index) => {
        const isDone = step.state === "done";
        const isActive = step.state === "active";

        return (
          <div
            key={`${step.title}-${index}`}
            className={
              isActive
                ? "rounded-[22px] border border-[rgba(0,68,136,0.26)] bg-[linear-gradient(135deg,rgba(0,68,136,0.12),rgba(255,255,255,0.72))] p-4"
                : isDone
                  ? "rounded-[22px] border border-[rgba(23,49,59,0.08)] bg-[linear-gradient(135deg,rgba(17,119,51,0.1),rgba(255,255,255,0.82))] p-4"
                  : "rounded-[22px] border border-[rgba(23,49,59,0.08)] bg-[linear-gradient(180deg,rgba(255,255,255,0.54),rgba(255,255,255,0.36))] p-4"
            }
          >
            <div className="flex items-start gap-3">
              <div
                className={
                  isActive
                    ? "mt-1 h-3 w-3 rounded-full bg-[var(--teal)] shadow-[0_0_0_6px_rgba(0,68,136,0.12)]"
                    : isDone
                      ? "mt-1 h-3 w-3 rounded-full bg-[var(--coral)] shadow-[0_0_0_6px_rgba(17,119,51,0.1)]"
                      : "mt-1 h-3 w-3 rounded-full bg-slate-300"
                }
              />
              <div>
                <p className="font-semibold text-slate-800">{step.title}</p>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  {step.description}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
