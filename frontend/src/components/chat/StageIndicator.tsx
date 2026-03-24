import { useSessionStore } from "../../stores/sessionStore";
import type { Stage } from "../../types/agent";

interface StageStep {
  key: Stage;
  label: string;
}

const STEPS: StageStep[] = [
  { key: "discover", label: "Discovering" },
  { key: "match", label: "Matching solution" },
  { key: "generate", label: "Generating code" },
];

const STAGE_ORDER: Stage[] = ["discover", "match", "generate", "done"];

export function StageIndicator() {
  const { stage, isStreaming } = useSessionStore();

  // hide only before any interaction has started
  if (stage === "discover" && !isStreaming) return null;

  // when done, push index beyond all steps so every step renders as past
  const currentIdx =
    stage === "done" ? STAGE_ORDER.length : STAGE_ORDER.indexOf(stage);

  return (
    <div className="px-4 py-2 bg-purple-50 border-b border-purple-100 flex items-center gap-1 overflow-x-auto">
      {STEPS.map((step, i) => {
        const stepIdx = STAGE_ORDER.indexOf(step.key);
        const isPast = currentIdx > stepIdx;
        const isCurrent = currentIdx === stepIdx;

        return (
          <div key={step.key} className="flex items-center gap-1 flex-shrink-0">
            <div className="flex items-center gap-1">
              <span
                className={`text-sm leading-none transition-colors ${isPast ? "text-teal-500" : isCurrent ? "text-purple-600" : "text-gray-300"}`}
              >
                ●
              </span>
              <span
                className={`text-xs font-medium transition-colors whitespace-nowrap ${isPast ? "text-teal-500 line-through decoration-teal-300" : isCurrent ? "text-purple-700" : "text-gray-300"}`}
              >
                {step.label}
                {isCurrent && isStreaming && (
                  <span className="animate-pulse">...</span>
                )}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <span
                className={`text-xs mx-1 ${isPast ? "text-teal-400" : "text-gray-200"}`}
              >
                →
              </span>
            )}
          </div>
        );
      })}

      {/* completion badge — only when fully done */}
      {stage === "done" && (
        <span className="ml-2 text-xs font-semibold text-teal-600 bg-teal-50 border border-teal-200 rounded-full px-2 py-0.5 flex-shrink-0">
          Code ready ✓
        </span>
      )}
    </div>
  );
}
