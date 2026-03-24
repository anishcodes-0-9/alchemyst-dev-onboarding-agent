import type { SlotStatus } from "../../hooks/useIntegration";

const colors: Record<SlotStatus, string> = {
  pending: "bg-gray-300",
  detected: "bg-amber-400",
  confirmed: "bg-teal-500",
};

export function StatusDot({ status }: { status: SlotStatus }) {
  return (
    <span className={`inline-block w-2 h-2 rounded-full ${colors[status]}`} />
  );
}
