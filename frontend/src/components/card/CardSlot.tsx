import { StatusDot } from "../shared/StatusDot";
import type { IntegrationSlot } from "../../hooks/useIntegration";

const displayLabels: Record<string, string> = {
  IntelliChat: "IntelliChat",
  ContextAPI: "Context API",
  ContextRouter: "Context Router",
  fastapi: "FastAPI",
  python: "Python",
  javascript: "JavaScript",
  java: "Java",
  chatbot: "Chatbot",
  rag: "RAG pipeline",
  agent: "Autonomous agent",
  openai_replace: "OpenAI replacement",
};

export function CardSlot({ slot }: { slot: IntegrationSlot }) {
  const displayValue = slot.value
    ? (displayLabels[slot.value] ?? slot.value)
    : null;

  return (
    <div className="flex items-start gap-3 py-3 border-b border-gray-50 last:border-0">
      <StatusDot status={slot.status} />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-400 mb-0.5">{slot.label}</p>
        {displayValue ? (
          <p className="text-sm font-medium text-gray-800 truncate">
            {displayValue}
          </p>
        ) : (
          <p className="text-sm text-gray-300">Waiting...</p>
        )}
      </div>
    </div>
  );
}
