import { useCallback, useRef } from "react";
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

  // (will wire properly after stream.ts fix)
  const controllerRef = useRef<AbortController | null>(null);

  // ✅ Token buffer
  const bufferRef = useRef("");
  const flushTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flushBuffer = useCallback(() => {
    if (bufferRef.current) {
      appendToken(bufferRef.current);
      bufferRef.current = "";
    }
    flushTimeoutRef.current = null;
  }, [appendToken]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      // (controller not active yet, will fix in next step)
      if (controllerRef.current) {
        controllerRef.current.abort();
      }

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
          onToken: (text) => {
            bufferRef.current += text;

            if (!flushTimeoutRef.current) {
              flushTimeoutRef.current = setTimeout(flushBuffer, 50);
            }
          },

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
          },

          onDone: () => {
            flushBuffer();

            useSessionStore.setState((state) => {
              const messages = [...state.messages];
              const last = messages[messages.length - 1];
              if (last?.role === "assistant") {
                messages[messages.length - 1] = {
                  ...last,
                  isStreaming: false,
                };
              }
              return { messages, isStreaming: false, stage: "done" };
            });
          },

          onError: (message) => {
            flushBuffer();

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
        flushBuffer();

        useSessionStore.setState((state) => {
          const messages = [...state.messages];
          const last = messages[messages.length - 1];
          if (last?.role === "assistant" && last.isStreaming) {
            messages[messages.length - 1] = {
              ...last,
              isStreaming: false,
            };
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
      flushBuffer,
    ],
  );

  return { sendMessage };
}
