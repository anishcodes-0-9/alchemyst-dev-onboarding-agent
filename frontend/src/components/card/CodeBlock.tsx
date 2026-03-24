import { useState, useEffect } from "react";
import { CopyButton } from "../shared/CopyButton";
import { DownloadButton } from "../shared/DownloadButton";
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
  const [activeTab, setActiveTab] = useState<Language>(codeLanguage);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    setActiveTab(codeLanguage);
  }, [codeLanguage]);

  const handleLanguageChange = async (lang: Language) => {
    if (lang === activeTab || isLoading) return;
    setActiveTab(lang);
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

  const displayCode =
    !expanded && generatedCode && generatedCode.split("\n").length > 20
      ? generatedCode.split("\n").slice(0, 20).join("\n") + "\n..."
      : generatedCode;

  return (
    <div className="mt-4">
      {/* toolbar */}
      <div className="flex items-center justify-between mb-2">
        <LanguageTabs
          active={activeTab}
          onChange={handleLanguageChange}
          disabled={isLoading}
        />
        <div className="flex items-center gap-1.5">
          {generatedCode && (
            <>
              <CopyButton text={generatedCode} />
              <DownloadButton code={generatedCode} language={activeTab} />
            </>
          )}
        </div>
      </div>

      {/* code area */}
      <div
        className={`bg-gray-950 rounded-xl overflow-hidden transition-all ${expanded ? "" : "max-h-64"}`}
      >
        <div className="overflow-x-auto overflow-y-auto max-h-full">
          {isLoading ? (
            <div className="p-4 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <p className="text-gray-500 text-xs font-mono">
                Generating code...
              </p>
            </div>
          ) : (
            <pre className="text-green-400 text-xs font-mono leading-relaxed whitespace-pre-wrap p-4">
              {displayCode}
            </pre>
          )}
        </div>
      </div>

      {/* expand/collapse toggle */}
      {generatedCode && generatedCode.split("\n").length > 20 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full mt-1 text-xs text-gray-400 hover:text-gray-600 py-1 transition-colors"
        >
          {expanded ? "↑ Show less" : "↓ Show more"}
        </button>
      )}
    </div>
  );
}
