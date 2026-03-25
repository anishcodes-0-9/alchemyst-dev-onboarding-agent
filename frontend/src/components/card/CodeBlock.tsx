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
  // hold previous code so block stays visible during language switch
  const [prevCode, setPrevCode] = useState<string>("");

  useEffect(() => {
    setActiveTab(codeLanguage);
  }, [codeLanguage]);

  // keep prevCode in sync whenever generatedCode has real content
  useEffect(() => {
    if (generatedCode) setPrevCode(generatedCode);
  }, [generatedCode]);

  const handleLanguageChange = async (lang: Language) => {
    if (lang === activeTab || isLoading) return;
    setActiveTab(lang);
    setCodeLanguage(lang);
    setIsLoading(true);
    // do NOT clear generatedCode here — keep old code visible while loading

    await generateCode(
      sessionId,
      lang,
      (snippet) => setGeneratedCode(snippet, lang),
      () => setIsLoading(false),
      () => setIsLoading(false),
    );
  };

  // show block if: we have current code, previous code (loading), or are loading
  const codeToDisplay = generatedCode || prevCode;
  if (!codeToDisplay && !isLoading) return null;

  const displayCode =
    !expanded && codeToDisplay && codeToDisplay.split("\n").length > 20
      ? codeToDisplay.split("\n").slice(0, 20).join("\n") + "\n..."
      : codeToDisplay;

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
          {codeToDisplay && (
            <>
              <CopyButton text={codeToDisplay} />
              <DownloadButton code={codeToDisplay} language={activeTab} />
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
            <div className="relative">
              {/* old code stays visible, dimmed */}
              <pre className="text-green-400 text-xs font-mono leading-relaxed whitespace-pre-wrap p-4 opacity-30">
                {displayCode}
              </pre>
              {/* loading overlay */}
              <div className="absolute inset-0 flex items-start pt-4 pl-4 gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse mt-0.5 flex-shrink-0" />
                <p className="text-gray-400 text-xs font-mono">
                  Generating {activeTab} code...
                </p>
              </div>
            </div>
          ) : (
            <pre className="text-green-400 text-xs font-mono leading-relaxed whitespace-pre-wrap p-4">
              {displayCode}
            </pre>
          )}
        </div>
      </div>

      {/* expand/collapse toggle */}
      {codeToDisplay && codeToDisplay.split("\n").length > 20 && (
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
