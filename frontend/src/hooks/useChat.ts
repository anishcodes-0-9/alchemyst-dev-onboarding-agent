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
            if (integration.language) {
              setCodeLanguage(integration.language);
            }
          },

          onCode: (snippet, language) => {
            setGeneratedCode(snippet, language);

            // Close the current assistant bubble, then open a fresh one
            // so the completion message token has a live bubble to land in.
            useSessionStore.setState((state) => {
              const messages = [...state.messages];
              const last = messages[messages.length - 1];
              if (last?.role === "assistant") {
                messages[messages.length - 1] = { ...last, isStreaming: false };
              }
              return {
                messages: [
                  ...messages,
                  {
                    id: uuidv4(),
                    role: "assistant",
                    content: "",
                    isStreaming: true,
                  },
                ],
              };
            });
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
        // always unlock input when stream ends
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
