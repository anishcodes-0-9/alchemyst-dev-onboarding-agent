interface DownloadButtonProps {
  code: string;
  language: string;
}

const extensions: Record<string, string> = {
  python: "py",
  javascript: "js",
  java: "java",
};

export function DownloadButton({ code, language }: DownloadButtonProps) {
  const handleDownload = () => {
    const ext = extensions[language] ?? "txt";
    const filename = `alchemyst-integration.${ext}`;
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={handleDownload}
      className="text-xs px-2.5 py-1 rounded-md border border-gray-200 text-gray-500 hover:bg-gray-50 hover:border-gray-300 transition-all font-medium"
    >
      Download
    </button>
  );
}
