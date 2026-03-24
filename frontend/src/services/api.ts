import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getSession = (sessionId: string) =>
  api.get(`/api/session/${sessionId}`);

export const deleteSession = (sessionId: string) =>
  api.delete(`/api/session/${sessionId}`);

export const generateCode = (
  sessionId: string,
  language: string,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError: (msg: string) => void,
) => {
  return fetch(`${BASE_URL}/api/generate-code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, language }),
  }).then(async (res) => {
    if (!res.ok) {
      onError("Request failed");
      return;
    }

    if (!res.body) {
      onError("No response body");
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";

    while (true) {
      const result = await reader.read();
      if (result.done) break;

      const chunk = result.value;
      if (!chunk) continue;

      buffer += decoder.decode(chunk, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (line.startsWith("data:")) {
          try {
            const payload = JSON.parse(line.slice(5).trim());

            if (payload.snippet) onChunk(payload.snippet);
            if (payload.sessionId) onDone();
            if (payload.message) onError(payload.message);
          } catch (e) {
            console.error("Stream parse error:", e);
          }
        }
      }
    }
  });
};
