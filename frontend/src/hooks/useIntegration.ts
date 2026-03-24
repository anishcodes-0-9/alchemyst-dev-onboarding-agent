import { useSessionStore } from "../stores/sessionStore";

export type SlotStatus = "pending" | "detected" | "confirmed";

export interface IntegrationSlot {
  label: string;
  value: string | null;
  status: SlotStatus;
}

export function useIntegration() {
  const { stage, integration, generatedCode, codeLanguage } = useSessionStore();

  const getStatus = (value: string | null): SlotStatus => {
    if (!value) return "pending";
    if (stage === "done" || stage === "generate") return "confirmed";
    return "detected";
  };

  const slots: IntegrationSlot[] = [
    {
      label: "Use case",
      value: integration.useCase,
      status: getStatus(integration.useCase),
    },
    {
      label: "Recommended feature",
      value: integration.feature,
      status: getStatus(integration.feature),
    },
    {
      label: "Tech stack",
      value: integration.stack,
      status: getStatus(integration.stack),
    },
  ];

  return { slots, generatedCode, codeLanguage, stage };
}
