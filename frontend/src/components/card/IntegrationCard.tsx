import { CardSlot } from "./CardSlot";
import { CodeBlock } from "./CodeBlock";
import { useIntegration } from "../../hooks/useIntegration";
import { useSessionStore } from "../../stores/sessionStore";

const stageLabels: Record<string, string> = {
  discover: "Discovering...",
  match: "Matching feature...",
  generate: "Generating code...",
  done: "Integration ready",
};

const featureDescriptions: Record<string, string> = {
  IntelliChat: "Streaming chat with built-in memory and thinking steps",
  ContextAPI: "Upload, search, and retrieve context across sessions",
  ContextRouter: "Drop-in OpenAI-compatible proxy — zero code changes",
};

export function IntegrationCard() {
  const { slots, generatedCode, stage } = useIntegration();
  const { integration } = useSessionStore();

  return (
    <div className="flex flex-col h-full bg-gray-50 px-5 py-5 overflow-y-auto">
      {/* header */}
      <div className="mb-4">
        <h2 className="text-sm font-semibold text-gray-800">
          Integration card
        </h2>
        <p className="text-xs text-gray-400 mt-0.5">{stageLabels[stage]}</p>
      </div>

      {/* progress bar */}
      <div className="w-full h-1 bg-gray-200 rounded-full mb-5">
        <div
          className="h-1 bg-purple-500 rounded-full transition-all duration-500"
          style={{
            width:
              stage === "discover"
                ? "15%"
                : stage === "match"
                  ? "50%"
                  : stage === "generate"
                    ? "75%"
                    : "100%",
          }}
        />
      </div>

      {/* slots */}
      <div className="bg-white rounded-xl border border-gray-100 px-4 py-1 mb-4">
        {slots.map((slot) => (
          <CardSlot key={slot.label} slot={slot} />
        ))}
      </div>

      {/* feature description */}
      {integration.feature && (
        <div className="bg-purple-50 border border-purple-100 rounded-xl px-4 py-3 mb-2">
          <p className="text-xs font-semibold text-purple-700 mb-1">
            {integration.feature}
          </p>
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
