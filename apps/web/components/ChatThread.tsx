'use client'

import { useEffect, useRef, useState, type FormEvent } from 'react'
import { ChatMessage } from '@/components/ChatMessage'
import { EmptyState } from '@/components/EmptyState'
import { ErrorBanner } from '@/components/ErrorBanner'
import { TypingIndicator } from '@/components/TypingIndicator'
import { useChat } from '@/hooks/useChat'
import { filledButton, typography } from '@/lib/theme'

/** Full chat experience: scrolling message thread plus a fixed input bar. */
export function ChatThread() {
  const { messages, loading, error, sendMessage, retry } = useChat()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const question = input.trim()
    if (question.length === 0 || loading) return
    setInput('')
    void sendMessage(question)
  }

  const lastMessage = messages[messages.length - 1]
  const awaitingFirstToken =
    loading && lastMessage?.role === 'assistant' && lastMessage.content === ''
  const visibleMessages = messages.filter(
    (message) => !(message.role === 'assistant' && message.content === ''),
  )

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-4 sm:px-6">
      <div className="flex-1 overflow-y-auto py-6">
        {visibleMessages.length === 0 && !loading ? (
          <EmptyState
            title="Ask your knowledge base"
            description="Ask a question about any document you've uploaded and get cited answers."
          />
        ) : (
          <div className="flex flex-col gap-4">
            {visibleMessages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {awaitingFirstToken ? <TypingIndicator /> : null}
          </div>
        )}

        {error ? (
          <div className="mt-4">
            <ErrorBanner message={error} onRetry={loading ? undefined : retry} />
          </div>
        ) : null}

        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="sticky bottom-0 flex items-center gap-2 bg-surface py-4"
      >
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask a question…"
          aria-label="Ask a question"
          disabled={loading}
          className={`${typography.body.large} flex-1 rounded-full border border-outline-variant bg-surface px-5 py-3 text-on-surface placeholder:text-on-surface-variant focus:border-primary focus:outline-none disabled:opacity-[0.38]`}
        />
        <button
          type="submit"
          disabled={loading || input.trim().length === 0}
          className={`${filledButton} px-6 py-3`}
        >
          Send
        </button>
      </form>
    </div>
  )
}
