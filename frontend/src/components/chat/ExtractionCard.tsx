import type { IntegrationState } from "../../types/agent";

interface ExtractionCardProps {
  integration: IntegrationState;
}

const useCaseLabels: Record<string, string> = {
  chatbot: "Conversational chatbot",
  rag: "RAG / document search",
  agent: "Autonomous agent workflow",
  openai_replace: "OpenAI API replacement",
};

const featureLabels: Record<string, { label: string; why: string }> = {
  IntelliChat: {
    label: "IntelliChat",
    why: "Best for conversational agents with built-in memory and streaming",
  },
  ContextAPI: {
    label: "Context API",
    why: "Best for storing, searching and retrieving context across sessions",
  },
  ContextRouter: {
    label: "Context Router",
    why: "Drop-in OpenAI-compatible proxy — zero code changes required",
  },
};

export function ExtractionCard({ integration }: ExtractionCardProps) {
  if (!integration.useCase && !integration.feature) return null;

  const featureInfo = integration.feature
    ? featureLabels[integration.feature]
    : null;

  return (
    <div className="flex justify-start mb-4">
      <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 flex-shrink-0">
        A
      </div>
      <div className="max-w-[78%] bg-white border border-purple-100 rounded-2xl rounded-bl-sm overflow-hidden shadow-sm">
        {/* header */}
        <div className="bg-purple-50 px-4 py-2.5 border-b border-purple-100">
          <p className="text-xs font-semibold text-purple-700 uppercase tracking-wide">
            Understanding your project
          </p>
        </div>

        {/* facts */}
        <div className="px-4 py-3 space-y-2">
          {integration.useCase && (
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0" />
              <div>
                <span className="text-xs text-gray-400">Use case</span>
                <p className="text-sm font-medium text-gray-800">
                  {useCaseLabels[integration.useCase] ?? integration.useCase}
                </p>
              </div>
            </div>
          )}

          {integration.stack && (
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0" />
              <div>
                <span className="text-xs text-gray-400">Stack</span>
                <p className="text-sm font-medium text-gray-800 capitalize">
                  {integration.stack}
                </p>
              </div>
            </div>
          )}

          {integration.features.length > 0 && (
            <div className="flex items-start gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0" />
              <div>
                <span className="text-xs text-gray-400">Requirements</span>
                <p className="text-sm font-medium text-gray-800 capitalize">
                  {integration.features.join(", ")}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* recommended feature */}
        {featureInfo && (
          <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
            <p className="text-xs text-gray-400 mb-1">Recommended feature</p>
            <p className="text-sm font-semibold text-purple-700">
              {featureInfo.label}
            </p>
            <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">
              {featureInfo.why}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
