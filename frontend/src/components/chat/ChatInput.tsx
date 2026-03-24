import { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-100 px-4 py-3 bg-white">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={
            disabled ? "Alex is thinking..." : "Tell me what you're building..."
          }
          rows={1}
          className="flex-1 resize-none rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 disabled:opacity-50 disabled:bg-gray-50 max-h-32 overflow-y-auto"
          style={{ minHeight: "40px" }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="flex-shrink-0 bg-purple-600 text-white rounded-xl px-4 py-2 text-sm font-medium hover:bg-purple-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
      <p className="text-xs text-gray-400 mt-1.5 ml-1">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
