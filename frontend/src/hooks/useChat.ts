import { useCallback } from "react";
import { useSessionStore } from "../stores/sessionStore";
import { streamChat } from "../services/stream";
import type { Language } from "../types/agent";
import { v4 as uuidv4 } from "uuid";

export function useChat() {
  const {
    sessionId,
    codeLanguage,
    addMessage,
    appendToken,
    setStreaming,
    setStage,
    setIntegration,
    setMemoryActive,
    setGeneratedCode,
    setCodeLanguage,
  } = useSessionStore();

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      addMessage({ id: uuidv4(), role: "user", content });
      addMessage({
        id: uuidv4(),
        role: "assistant",
        content: "",
        isStreaming: true,
      });

      setStreaming(true);

      try {
        await streamChat(sessionId, content, codeLanguage as Language, {
          onToken: (text) => appendToken(text),

          onStageUpdate: (stage, integration, memoryActive) => {
            setStage(stage);
            setIntegration(integration);
            if (memoryActive !== undefined) setMemoryActive(memoryActive);
            // sync language from backend integration state
            if (integration.language) {
              setCodeLanguage(integration.language);
            }
          },

          onCode: (snippet, language) => {
            setGeneratedCode(snippet, language);
          },

          onDone: () => {
            useSessionStore.setState((state) => {
              const messages = [...state.messages];
              const last = messages[messages.length - 1];
              if (last?.role === "assistant") {
                messages[messages.length - 1] = { ...last, isStreaming: false };
              }
              return { messages, isStreaming: false, stage: "done" };
            });
          },

          onError: (message) => {
            useSessionStore.setState((state) => {
              const messages = [...state.messages];
              const last = messages[messages.length - 1];
              if (last?.role === "assistant") {
                messages[messages.length - 1] = {
                  ...last,
                  content: `Error: ${message}`,
                  isStreaming: false,
                };
              }
              return { messages, isStreaming: false };
            });
          },
        });
      } finally {
        // CRITICAL: always unlock input when stream ends
        // covers the case where agent stays in discover (no done event)
        useSessionStore.setState((state) => {
          const messages = [...state.messages];
          const last = messages[messages.length - 1];
          if (last?.role === "assistant" && last.isStreaming) {
            messages[messages.length - 1] = { ...last, isStreaming: false };
          }
          return { messages, isStreaming: false };
        });
      }
    },
    [
      sessionId,
      codeLanguage,
      addMessage,
      appendToken,
      setStreaming,
      setStage,
      setIntegration,
      setMemoryActive,
      setGeneratedCode,
      setCodeLanguage,
    ],
  );

  return { sendMessage };
}
