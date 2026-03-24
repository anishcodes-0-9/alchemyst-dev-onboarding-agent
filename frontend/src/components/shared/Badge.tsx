interface BadgeProps {
  label: string;
  variant?: "purple" | "teal" | "amber" | "gray";
}

const variants = {
  purple: "bg-purple-100 text-purple-800",
  teal: "bg-teal-100 text-teal-800",
  amber: "bg-amber-100 text-amber-800",
  gray: "bg-gray-100 text-gray-600",
};

export function Badge({ label, variant = "gray" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${variants[variant]}`}
    >
      {label}
    </span>
  );
}
