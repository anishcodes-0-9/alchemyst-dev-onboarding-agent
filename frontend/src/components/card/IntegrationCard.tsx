import { CardSlot } from "./CardSlot";
import { CodeBlock } from "./CodeBlock";
import { useIntegration } from "../../hooks/useIntegration";
import { useSessionStore } from "../../stores/sessionStore";

const stages = ["discover", "match", "generate", "done"] as const;

const stageConfig = {
  discover: {
    label: "Understanding requirements",
    color: "text-purple-600 bg-purple-50 border-purple-200",
  },
  match: {
    label: "Structuring solution",
    color: "text-amber-600 bg-amber-50 border-amber-200",
  },
  generate: {
    label: "Generating code",
    color: "text-teal-600 bg-teal-50 border-teal-200",
  },
  done: {
    label: "Integration ready",
    color: "text-teal-600 bg-teal-50 border-teal-200",
  },
};

const featureDescriptions: Record<string, string> = {
  IntelliChat: "Streaming chat with built-in memory and thinking steps",
  ContextAPI: "Upload, search, and retrieve context across sessions",
  ContextRouter: "Drop-in OpenAI-compatible proxy — zero code changes",
};

export function IntegrationCard() {
  const { slots, generatedCode, stage } = useIntegration();
  const { integration, isStreaming } = useSessionStore();

  const currentStageIndex = stages.indexOf(stage as (typeof stages)[number]);

  return (
    <div className="flex flex-col h-full bg-gray-50 px-5 py-5 overflow-y-auto">
      {/* stage pipeline */}
      <div className="mb-5">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
          Pipeline
        </p>
        <div className="space-y-2">
          {stages
            .filter((s) => s !== "done")
            .map((s, i) => {
              const isPast = currentStageIndex > i;
              const isCurrent = stage === s || (stage === "done" && i === 2);
              const isFuture = currentStageIndex < i && stage !== "done";

              return (
                <div key={s} className="flex items-center gap-2.5">
                  <div
                    className={`w-2 h-2 rounded-full flex-shrink-0 transition-all ${
                      isPast || stage === "done"
                        ? "bg-teal-500"
                        : isCurrent && isStreaming
                          ? "bg-purple-500 animate-pulse"
                          : isCurrent
                            ? "bg-purple-500"
                            : "bg-gray-300"
                    }`}
                  />
                  <span
                    className={`text-xs font-medium transition-all ${
                      isPast || stage === "done"
                        ? "text-teal-600 line-through decoration-teal-300"
                        : isCurrent
                          ? "text-gray-800"
                          : isFuture
                            ? "text-gray-300"
                            : "text-gray-400"
                    }`}
                  >
                    {stageConfig[s].label}
                  </span>
                  {isCurrent && isStreaming && (
                    <span className="text-xs text-purple-400 animate-pulse">
                      ...
                    </span>
                  )}
                  {(isPast || stage === "done") && (
                    <span className="text-xs text-teal-500">✓</span>
                  )}
                </div>
              );
            })}
        </div>
      </div>

      <div className="w-full h-px bg-gray-200 mb-4" />

      {/* slots */}
      <div className="bg-white rounded-xl border border-gray-100 px-4 py-1 mb-4">
        {slots.map((slot) => (
          <CardSlot key={slot.label} slot={slot} />
        ))}
      </div>

      {/* feature description */}
      {integration.feature && (
        <div className="bg-purple-50 border border-purple-100 rounded-xl px-4 py-3 mb-4">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-purple-700">
              {integration.feature}
            </span>
            <span className="text-xs px-1.5 py-0.5 rounded bg-purple-100 text-purple-600 font-medium">
              Recommended
            </span>
          </div>
          <p className="text-xs text-purple-600 leading-relaxed">
            {featureDescriptions[integration.feature]}
          </p>
        </div>
      )}

      {/* code block */}
      {generatedCode && <CodeBlock />}

      {/* empty state */}
      {!generatedCode && stage === "discover" && (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-xs text-gray-300 text-center leading-relaxed">
            Your integration details
            <br />
            will appear here as Alex
            <br />
            learns about your project
          </p>
        </div>
      )}
    </div>
  );
}
