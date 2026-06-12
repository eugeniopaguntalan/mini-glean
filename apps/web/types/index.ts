/**
 * Frontend type definitions for MiniGlean.
 *
 * These mirror the canonical shared types in `packages/shared/types.ts` and the
 * FastAPI response schemas. They are kept local to the web app so the module
 * graph stays self-contained (no cross-package imports) while remaining strictly
 * typed end to end.
 */

/** The kind of source a document was ingested from. */
export type DocumentType = 'pdf' | 'url' | 'note'

/** Who authored a chat message. */
export type ChatRole = 'user' | 'assistant'

/** A document stored in the knowledge base (matches `DocumentResponse`). */
export interface Document {
  id: string
  filename: string
  type: DocumentType
  tags: string[]
  chunk_count: number
  created_at: string
}

/** A single cited source attached to an assistant message. */
export interface SourceCitation {
  doc_id: string
  filename: string
  excerpt: string
  chunk_index?: number
}

/** A message in a chat conversation. */
export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  sources: SourceCitation[]
  created_at: string
}

/** Full (non-streaming) chat response from `POST /chat`. */
export interface ChatResponse {
  id: string
  content: string
  sources: SourceCitation[]
  created_at: string
  session_id: string
}

/** Normalized error surfaced from the API client. */
export interface ApiError {
  detail: string
  status: number
}
