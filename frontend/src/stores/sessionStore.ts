import { create } from "zustand";
import type {
  Message,
  Stage,
  IntegrationState,
  Language,
} from "../types/agent";

const DEFAULT_INTEGRATION: IntegrationState = {
  useCase: null,
  stack: null,
  feature: null,
  architecture: null,
  code: null,
  language: "python",
  features: [],
  no_op: false,
};

interface SessionStore {
  sessionId: string;
  messages: Message[];
  isStreaming: boolean;
  stage: Stage;
  integration: IntegrationState;
  memoryActive: boolean;
  generatedCode: string | null;
  codeLanguage: Language;

  // actions
  setSessionId: (id: string) => void;
  addMessage: (msg: Message) => void;
  appendToken: (text: string) => void;
  setStreaming: (val: boolean) => void;
  setStage: (stage: Stage) => void;
  setIntegration: (integration: IntegrationState) => void;
  setMemoryActive: (val: boolean) => void;
  setGeneratedCode: (code: string, language: Language) => void;
  setCodeLanguage: (language: Language) => void;
  resetSession: () => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessionId: crypto.randomUUID(),
  messages: [],
  isStreaming: false,
  stage: "discover",
  integration: DEFAULT_INTEGRATION,
  memoryActive: false,
  generatedCode: null,
  codeLanguage: "python",

  setSessionId: (id) => set({ sessionId: id }),

  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),

  appendToken: (text) =>
    set((state) => {
      const messages = [...state.messages];
      const last = messages[messages.length - 1];
      if (last && last.role === "assistant" && last.isStreaming) {
        messages[messages.length - 1] = {
          ...last,
          content: last.content + text,
        };
      }
      return { messages };
    }),

  setStreaming: (val) => set({ isStreaming: val }),

  setStage: (stage) => set({ stage }),

  setIntegration: (integration) => set({ integration }),

  setMemoryActive: (val) => set({ memoryActive: val }),

  setGeneratedCode: (code, language) =>
    set({ generatedCode: code, codeLanguage: language }),

  setCodeLanguage: (language) => set({ codeLanguage: language }),

  resetSession: () =>
    set({
      sessionId: crypto.randomUUID(),
      messages: [],
      isStreaming: false,
      stage: "discover",
      integration: DEFAULT_INTEGRATION,
      memoryActive: false,
      generatedCode: null,
      codeLanguage: "python",
    }),
}));
