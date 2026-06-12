/**
 * API Client
 *
 * The single place where the frontend talks to the FastAPI backend.
 * No component or hook should call `fetch` directly — everything routes
 * through the typed functions exported here.
 */

import type { ApiError, ChatResponse, Document } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Build an {@link ApiError} for a failed `fetch` (the request never reached the
 * server). Distinguishes a dropped internet connection from an unreachable
 * backend so the UI can show an actionable message.
 */
function networkError(): ApiError {
  if (typeof navigator !== 'undefined' && navigator.onLine === false) {
    return { detail: 'No internet connection.', status: 0 }
  }
  return { detail: 'Cannot reach the server. Please try again.', status: 0 }
}

/** Build a normalized {@link ApiError} from a non-OK response. */
async function toApiError(response: Response): Promise<ApiError> {
  let detail = response.statusText || 'Request failed'
  try {
    const body = await response.text()
    if (body) {
      try {
        const parsed = JSON.parse(body) as { detail?: unknown }
        detail =
          typeof parsed.detail === 'string' ? parsed.detail : body
      } catch {
        detail = body
      }
    }
  } catch {
    // Ignore body read failures; fall back to status text.
  }
  return { detail, status: response.status }
}

/** Perform a JSON request and parse the response, throwing {@link ApiError}. */
async function requestJson<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })
  } catch {
    throw networkError()
  }

  if (!response.ok) {
    throw await toApiError(response)
  }

  return response.json() as Promise<T>
}

/** GET /documents — list every document in the knowledge base. */
export function listDocuments(): Promise<Document[]> {
  return requestJson<Document[]>('/documents', { method: 'GET' })
}

/** POST /documents/upload/pdf — upload a PDF file (multipart). */
export async function uploadPdf(file: File): Promise<Document> {
  const form = new FormData()
  form.append('file', file)

  let response: Response
  try {
    response = await fetch(`${API_URL}/documents/upload/pdf`, {
      method: 'POST',
      body: form,
    })
  } catch {
    throw networkError()
  }

  if (!response.ok) {
    throw await toApiError(response)
  }

  return response.json() as Promise<Document>
}

/** POST /documents/url — ingest a web page by URL. */
export function ingestUrl(url: string): Promise<Document> {
  return requestJson<Document>('/documents/url', {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}

/** POST /documents/note — save a plain-text note. */
export function addNote(content: string, tags: string[] = []): Promise<Document> {
  return requestJson<Document>('/documents/note', {
    method: 'POST',
    body: JSON.stringify({ content, tags }),
  })
}

/** DELETE /documents/{id} — remove a document and its chunks (204, no body). */
export async function deleteDocument(id: string): Promise<void> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/documents/${id}`, { method: 'DELETE' })
  } catch {
    throw networkError()
  }

  if (!response.ok) {
    throw await toApiError(response)
  }
}

/** POST /chat — non-streaming question answering (full response at once). */
export function chat(question: string, sessionId: string): Promise<ChatResponse> {
  return requestJson<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({ question, session_id: sessionId }),
  })
}

/**
 * Sentinel prefix the backend uses to deliver final source citations as a
 * single JSON SSE event once the answer has finished streaming.
 */
export const SOURCES_PREFIX = '[SOURCES]'

/**
 * Sentinel prefix the backend uses to report a mid-stream failure (for example
 * a rate limit) once streaming has already started with a `200` response.
 */
export const ERROR_PREFIX = '[ERROR]'

/**
 * POST /chat/stream — stream the assistant's answer token by token via SSE.
 *
 * Yields each `data:` payload from the stream in order. Answer tokens are
 * yielded as plain text; once the answer completes, a single payload prefixed
 * with {@link SOURCES_PREFIX} carries the JSON-encoded citations. The terminal
 * `[DONE]` marker ends the generator and is not yielded.
 */
export async function* streamChat(
  question: string,
  sessionId: string,
): AsyncGenerator<string, void, unknown> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, session_id: sessionId }),
    })
  } catch {
    throw networkError()
  }

  if (!response.ok) {
    throw await toApiError(response)
  }
  if (!response.body) {
    throw { detail: 'Streaming is not supported by this browser.', status: 0 } as ApiError
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // SSE events are separated by a blank line.
      const events = buffer.split('\n\n')
      buffer = events.pop() ?? ''

      for (const event of events) {
        const payload = event
          .split('\n')
          .filter((line) => line.startsWith('data:'))
          .map((line) => line.slice(line.startsWith('data: ') ? 6 : 5))
          .join('\n')

        if (payload === '[DONE]') return
        if (payload.startsWith(ERROR_PREFIX)) {
          throw {
            detail: payload.slice(ERROR_PREFIX.length),
            status: 0,
          } as ApiError
        }
        if (payload.length > 0) yield payload
      }
    }
  } finally {
    reader.releaseLock()
  }
}

