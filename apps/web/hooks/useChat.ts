'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { SOURCES_PREFIX, streamChat } from '@/lib/api'
import type { ApiError, ChatMessage, SourceCitation } from '@/types'

interface UseChatResult {
  messages: ChatMessage[]
  loading: boolean
  error: string | null
  sendMessage: (question: string) => Promise<void>
  retry: () => Promise<void>
}

/** Reject questions longer than this to avoid runaway prompts. */
const MAX_QUESTION_LENGTH = 2000

function errorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'detail' in err) {
    return (err as ApiError).detail
  }
  return 'Something went wrong. Please try again.'
}

function createId(): string {
  return crypto.randomUUID()
}

function parseSources(payload: string): SourceCitation[] {
  try {
    const parsed: unknown = JSON.parse(payload.slice(SOURCES_PREFIX.length))
    return Array.isArray(parsed) ? (parsed as SourceCitation[]) : []
  } catch {
    return []
  }
}

/**
 * Manages a streaming chat conversation.
 *
 * A stable `session_id` is created once on mount. `sendMessage` appends the
 * user turn, opens an SSE stream, and appends assistant tokens to a single
 * message in real time. Source citations arrive as a final event and are
 * attached once the stream completes.
 */
export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const sessionId = useRef<string>('')
  const loadingRef = useRef<boolean>(false)
  const lastQuestion = useRef<string>('')

  useEffect(() => {
    sessionId.current = createId()
  }, [])

  // Keep a ref of loading so sendMessage can guard re-entry without a dep cycle.
  useEffect(() => {
    loadingRef.current = loading
  }, [loading])

  const sendMessage = useCallback(async (question: string) => {
    const trimmed = question.trim()
    if (trimmed.length === 0 || loadingRef.current) return

    if (trimmed.length > MAX_QUESTION_LENGTH) {
      setError(
        `Question is too long (max ${MAX_QUESTION_LENGTH} characters). Please shorten it.`,
      )
      return
    }

    lastQuestion.current = trimmed

    const userMessage: ChatMessage = {
      id: createId(),
      role: 'user',
      content: trimmed,
      sources: [],
      created_at: new Date().toISOString(),
    }

    const assistantId = createId()
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      sources: [],
      created_at: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage, assistantMessage])
    setLoading(true)
    setError(null)

    try {
      for await (const payload of streamChat(trimmed, sessionId.current)) {
        if (payload.startsWith(SOURCES_PREFIX)) {
          const sources = parseSources(payload)
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, sources } : msg,
            ),
          )
        } else {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? { ...msg, content: msg.content + payload }
                : msg,
            ),
          )
        }
      }
    } catch (err) {
      setError(errorMessage(err))
      // Drop the empty assistant placeholder if nothing streamed.
      setMessages((prev) =>
        prev.filter((msg) => !(msg.id === assistantId && msg.content === '')),
      )
    } finally {
      setLoading(false)
    }
  }, [])

  const retry = useCallback(async () => {
    if (lastQuestion.current.length > 0) {
      await sendMessage(lastQuestion.current)
    }
  }, [sendMessage])

  return { messages, loading, error, sendMessage, retry }
}
