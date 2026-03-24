import type { Message } from "../../types/agent";

function cleanContent(content: string): string {
  // remove [EXTRACTED] block from displayed message
  return content.replace(/\[EXTRACTED\][^\n]*/g, "").trim();
}

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const displayContent = isUser
    ? message.content
    : cleanContent(message.content);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 flex-shrink-0">
          A
        </div>
      )}
      <div
        className={`max-w-[78%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "bg-purple-600 text-white rounded-br-sm"
            : "bg-gray-100 text-gray-800 rounded-bl-sm"
        }`}
      >
        {displayContent === "" && message.isStreaming ? (
          <span className="flex items-center gap-1 py-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
            <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" />
          </span>
        ) : (
          <>
            <span className="whitespace-pre-wrap">{displayContent}</span>
            {message.isStreaming && displayContent && (
              <span className="inline-block w-0.5 h-3.5 bg-gray-500 ml-0.5 align-middle animate-pulse" />
            )}
          </>
        )}
      </div>
    </div>
  );
}
