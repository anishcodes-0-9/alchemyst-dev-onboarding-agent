export function Spinner() {
  return (
    <div className="flex items-center gap-1">
      <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
      <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
      <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce" />
    </div>
  );
}
