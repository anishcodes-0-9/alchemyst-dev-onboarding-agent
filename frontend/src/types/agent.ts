export type Stage = "discover" | "match" | "generate" | "done";

export type Feature = "IntelliChat" | "ContextAPI" | "ContextRouter" | null;

export type Language = "python" | "javascript" | "java";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

export interface IntegrationState {
  useCase: string | null;
  stack: string | null;
  feature: Feature;
  architecture: string | null;
  code: string | null;
  language: Language;
  features: string[];
  no_op: boolean;
}

export interface SessionState {
  sessionId: string;
  stage: Stage;
  integration: IntegrationState;
  memoryActive: boolean;
  historyLength: number;
}

export interface SSETokenEvent {
  type: "token";
  text: string;
}

export interface SSEStageUpdateEvent {
  type: "stage_update";
  stage: Stage;
  integration: IntegrationState;
  memoryActive?: boolean;
}

export interface SSECodeEvent {
  type: "code";
  snippet: string;
  language: Language;
}

export interface SSEDoneEvent {
  type: "done";
  sessionId: string;
}

export interface SSEErrorEvent {
  type: "error";
  message: string;
}

export type SSEEvent =
  | SSETokenEvent
  | SSEStageUpdateEvent
  | SSECodeEvent
  | SSEDoneEvent
  | SSEErrorEvent;
