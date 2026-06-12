/** Three bouncing dots in an assistant-style bubble shown while streaming. */
export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div
        className="flex items-center gap-1 rounded-xl rounded-bl-sm bg-surface px-4 py-3 shadow-sm"
        role="status"
        aria-label="Assistant is typing"
      >
        <span className="h-2 w-2 animate-bounce rounded-full bg-on-surface-variant [animation-delay:-0.3s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-on-surface-variant [animation-delay:-0.15s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-on-surface-variant" />
      </div>
    </div>
  )
}
