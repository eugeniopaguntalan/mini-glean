import { SourceCitation } from '@/components/SourceCitation'
import { typography } from '@/lib/theme'
import type { ChatMessage as ChatMessageType } from '@/types'

interface ChatMessageProps {
  message: ChatMessageType
}

/** A single chat bubble — user (right) or assistant (left) with citations. */
export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div
          className={`${typography.body.large} max-w-[80%] whitespace-pre-wrap break-words rounded-xl rounded-br-sm bg-primary px-4 py-2.5 text-on-primary`}
        >
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <div
        className={`${typography.body.large} max-w-[80%] whitespace-pre-wrap break-words rounded-xl rounded-bl-sm bg-surface px-4 py-2.5 text-on-surface shadow-sm`}
      >
        {message.content}
      </div>

      {message.sources.length > 0 ? (
        <div className="flex max-w-[80%] flex-wrap gap-2">
          {message.sources.map((citation) => (
            <SourceCitation
              key={`${citation.doc_id}-${citation.chunk_index ?? 0}`}
              citation={citation}
            />
          ))}
        </div>
      ) : null}
    </div>
  )
}
