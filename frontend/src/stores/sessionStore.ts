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

const STORAGE_KEY = "alchemyst_session_id";

function getPersistedSessionId(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) || crypto.randomUUID();
  } catch {
    return crypto.randomUUID();
  }
}
function persistSessionId(id: string) {
  if (typeof window !== "undefined" && window.localStorage) {
    window.localStorage.setItem(STORAGE_KEY, id);
  }
}

interface SessionStore {
  sessionId: string;
  messages: Message[];
  isStreaming: boolean;
  stage: Stage;
  integration: IntegrationState;
  memoryActive: boolean;
  generatedCode: string | null;
  codeLanguage: Language;

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
  sessionId: getPersistedSessionId(),
  messages: [],
  isStreaming: false,
  stage: "discover",
  integration: DEFAULT_INTEGRATION,
  memoryActive: false,
  generatedCode: null,
  codeLanguage: "python",

  setSessionId: (id) => {
    persistSessionId(id);
    set({ sessionId: id });
  },

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

  resetSession: () => {
    const newId = crypto.randomUUID();
    persistSessionId(newId);
    set({
      sessionId: newId,
      messages: [],
      isStreaming: false,
      stage: "discover",
      integration: DEFAULT_INTEGRATION,
      memoryActive: false,
      generatedCode: null,
      codeLanguage: "python",
    });
  },
}));
