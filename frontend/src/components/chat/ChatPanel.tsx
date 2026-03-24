import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { StageIndicator } from "./StageIndicator";
import { useSessionStore } from "../../stores/sessionStore";
import { useChat } from "../../hooks/useChat";
import { Badge } from "../shared/Badge";

export function ChatPanel() {
  const { messages, isStreaming, memoryActive, resetSession } =
    useSessionStore();
  const { sendMessage } = useChat();

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-100">
      {/* header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-purple-600 flex items-center justify-center text-white text-xs font-bold">
            A
          </div>
          <div>
            <p className="text-sm font-medium text-gray-800">Alex</p>
            <p className="text-xs text-gray-400">
              Alchemyst Integration Engineer
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {memoryActive && <Badge label="Memory active" variant="teal" />}
          <button
            onClick={resetSession}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          >
            Start over
          </button>
        </div>
      </div>

      {/* stage indicator */}
      <StageIndicator />

      {/* messages */}
      <MessageList messages={messages} />

      {/* input */}
      <ChatInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
