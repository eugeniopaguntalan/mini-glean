/**
 * Shared TypeScript types for MiniGlean
 * Used by both frontend and backend (if TypeScript is added)
 */

export interface Document {
  id: string
  filename: string
  type: 'pdf' | 'url' | 'note'
  tags: string[]
  chunk_count: number
  created_at: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources: SourceCitation[]
  created_at: string
}

export interface SourceCitation {
  doc_id: string
  filename: string
  excerpt: string
  chunk_index?: number
}

export interface HealthResponse {
  status: 'ok' | 'degraded'
  database: 'connected' | 'disconnected'
  environment: string
  error?: string
}

export interface ApiError {
  detail: string
  status: number
}

export interface DocumentUploadRequest {
  filename: string
  type: 'pdf' | 'url' | 'note'
  content?: string
  url?: string
  tags?: string[]
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
}

export interface ChatRequest {
  message: string
  conversation_id?: string
}

export interface ChatResponse {
  message: ChatMessage
  conversation_id: string
}
