import { useState } from "react";
import { CopyButton } from "../shared/CopyButton";
import { LanguageTabs } from "./LanguageTabs";
import { generateCode } from "../../services/api";
import { useSessionStore } from "../../stores/sessionStore";
import type { Language } from "../../types/agent";

export function CodeBlock() {
  const {
    sessionId,
    generatedCode,
    codeLanguage,
    setGeneratedCode,
    setCodeLanguage,
  } = useSessionStore();
  const [isLoading, setIsLoading] = useState(false);

  const handleLanguageChange = async (lang: Language) => {
    if (lang === codeLanguage || isLoading) return;
    setCodeLanguage(lang);
    setIsLoading(true);
    setGeneratedCode("", lang);

    await generateCode(
      sessionId,
      lang,
      (snippet) => setGeneratedCode(snippet, lang),
      () => setIsLoading(false),
      () => setIsLoading(false),
    );
  };

  if (!generatedCode && !isLoading) return null;

  return (
    <div className="mt-4">
      <div className="flex items-center justify-between mb-2">
        <LanguageTabs
          active={codeLanguage}
          onChange={handleLanguageChange}
          disabled={isLoading}
        />
        {generatedCode && <CopyButton text={generatedCode} />}
      </div>
      <div className="bg-gray-950 rounded-xl p-4 overflow-x-auto">
        {isLoading ? (
          <p className="text-gray-500 text-xs font-mono">Generating...</p>
        ) : (
          <pre className="text-green-400 text-xs font-mono leading-relaxed whitespace-pre-wrap">
            {generatedCode}
          </pre>
        )}
      </div>
    </div>
  );
}
