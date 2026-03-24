import type { Language, IntegrationState, Stage } from "../types/agent";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface StreamCallbacks {
  onToken: (text: string) => void;
  onStageUpdate: (
    stage: Stage,
    integration: IntegrationState,
    memoryActive?: boolean,
  ) => void;
  onCode: (snippet: string, language: Language) => void;
  onDone: (sessionId: string) => void;
  onError: (message: string) => void;
}

export async function streamChat(
  sessionId: string,
  message: string,
  language: Language,
  callbacks: StreamCallbacks,
): Promise<void> {
  const response = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, message, language }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: "Unknown error" }));
    callbacks.onError(err.error || "Request failed");
    return;
  }

  if (!response.body) {
    callbacks.onError("No response body");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";
  let currentEvent = "";

  while (true) {
    const result = await reader.read();
    if (result.done) break;

    const chunk = result.value;
    if (!chunk) continue;

    buffer += decoder.decode(chunk, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        const raw = line.slice(5).trim();

        try {
          const payload = JSON.parse(raw);

          switch (currentEvent) {
            case "token":
              callbacks.onToken(payload.text);
              break;

            case "stage_update":
              callbacks.onStageUpdate(
                payload.stage,
                payload.integration,
                payload.memoryActive,
              );
              break;

            case "code":
              callbacks.onCode(payload.snippet, payload.language);
              break;

            case "done":
              callbacks.onDone(payload.sessionId);
              break;

            case "error":
              callbacks.onError(payload.message);
              break;
          }
        } catch (e) {
          console.error("Stream parse error:", e);
        }

        currentEvent = "";
      }
    }
  }
}
