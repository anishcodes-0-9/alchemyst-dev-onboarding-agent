import { Spinner } from "../shared/Spinner";
import type { Message } from "../../types/agent";

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "bg-purple-600 text-white rounded-br-sm"
            : "bg-gray-100 text-gray-800 rounded-bl-sm"
        }`}
      >
        {message.content || (message.isStreaming ? <Spinner /> : "")}
        {message.isStreaming && message.content && (
          <span className="inline-block w-0.5 h-3.5 bg-gray-400 ml-0.5 animate-pulse align-middle" />
        )}
      </div>
    </div>
  );
}
