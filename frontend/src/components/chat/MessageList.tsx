import { useEffect, useRef } from "react";
import { MessageBubble } from "./MessageBubble";
import { ExtractionCard } from "./ExtractionCard";
import { useSessionStore } from "../../stores/sessionStore";
import type { Message } from "../../types/agent";

export function MessageList({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const { stage, integration } = useSessionStore();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, stage]);

  const showExtractionCard =
    (stage === "generate" || stage === "done") && integration.useCase;

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-400 text-sm text-center">
            Tell Alex what you're building to get started
          </p>
        </div>
      )}

      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {/* show structured extraction card when we have enough info */}
      {showExtractionCard && <ExtractionCard integration={integration} />}

      <div ref={bottomRef} />
    </div>
  );
}
