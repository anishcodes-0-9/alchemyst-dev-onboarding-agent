import type { Language } from "../../types/agent";

const LANGUAGES: { value: Language; label: string }[] = [
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "java", label: "Java" },
];

interface LanguageTabsProps {
  active: Language;
  onChange: (lang: Language) => void;
  disabled?: boolean;
}

export function LanguageTabs({
  active,
  onChange,
  disabled,
}: LanguageTabsProps) {
  return (
    <div className="flex gap-1">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.value}
          onClick={() => onChange(lang.value)}
          disabled={disabled}
          className={`px-3 py-1 text-xs rounded-md font-medium transition-colors disabled:opacity-40 ${
            active === lang.value
              ? "bg-purple-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
