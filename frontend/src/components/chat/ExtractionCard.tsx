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
    why: "Streaming chat with built-in memory — no message history management needed",
  },
  ContextAPI: {
    label: "Context API",
    why: "Semantic upload + retrieval across sessions — no vector DB required",
  },
  ContextRouter: {
    label: "Context Router",
    why: "Drop-in OpenAI proxy — two config lines to migrate, zero code changes",
  },
};

const stackLabels: Record<string, string> = {
  "python / fastapi": "Python / FastAPI",
  "node / express": "Node.js / Express",
  "java / spring boot": "Java / Spring Boot",
  fastapi: "FastAPI",
  python: "Python",
  javascript: "JavaScript",
  java: "Java",
  flask: "Flask",
  django: "Django",
  express: "Express",
  spring: "Spring Boot",
};

const TAG_COLORS = [
  "bg-purple-100 text-purple-700",
  "bg-teal-100 text-teal-700",
  "bg-blue-100 text-blue-700",
  "bg-amber-100 text-amber-700",
];

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
        <div className="bg-purple-50 px-4 py-2.5 border-b border-purple-100">
          <p className="text-xs font-semibold text-purple-700 uppercase tracking-wide">
            Understanding your project
          </p>
        </div>

        <div className="px-4 py-3 space-y-2.5">
          {integration.useCase && (
            <div>
              <p className="text-xs text-gray-400 mb-0.5">Use case</p>
              <p className="text-sm font-medium text-gray-800">
                {useCaseLabels[integration.useCase] ?? integration.useCase}
              </p>
            </div>
          )}

          {integration.stack && (
            <div>
              <p className="text-xs text-gray-400 mb-0.5">Stack</p>
              <p className="text-sm font-medium text-gray-800">
                {stackLabels[integration.stack] ?? integration.stack}
              </p>
            </div>
          )}

          {integration.features.length > 0 && (
            <div>
              <p className="text-xs text-gray-400 mb-1.5">Requirements</p>
              <div className="flex flex-wrap gap-1.5">
                {integration.features.map((f, i) => (
                  <span
                    key={f}
                    className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${
                      TAG_COLORS[i % TAG_COLORS.length]
                    }`}
                  >
                    {f}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

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
