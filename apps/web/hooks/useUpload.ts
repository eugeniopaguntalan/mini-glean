'use client'

import { useCallback, useState } from 'react'
import { addNote, ingestUrl, uploadPdf } from '@/lib/api'
import type { ApiError, Document } from '@/types'

/** The three ingest modes surfaced in the upload panel. */
export type UploadMode = 'pdf' | 'url' | 'note'

/** Lifecycle status of an upload attempt. */
export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

const MAX_PDF_BYTES = 10 * 1024 * 1024 // 10 MB

interface UseUploadOptions {
  /** Called with the newly created document after a successful ingest. */
  onSuccess?: (document: Document) => void
  /** Called when an ingest attempt fails (including client-side validation). */
  onError?: () => void
}

interface UseUploadResult {
  status: UploadStatus
  error: string | null
  submitPdf: (file: File) => Promise<void>
  submitUrl: (url: string) => Promise<void>
  submitNote: (content: string, tags: string[]) => Promise<void>
  reset: () => void
}

function errorMessage(err: unknown, fallback: string): string {
  if (err && typeof err === 'object' && 'detail' in err) {
    return (err as ApiError).detail
  }
  return fallback
}

function isValidUrl(value: string): boolean {
  try {
    const parsed = new URL(value)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

/**
 * Drives the upload panel: validates input client-side, calls the matching
 * API function, and tracks idle / uploading / success / error states. On
 * success it fires `onSuccess` so the document library can refetch.
 */
export function useUpload({ onSuccess, onError }: UseUploadOptions = {}): UseUploadResult {
  const [status, setStatus] = useState<UploadStatus>('idle')
  const [error, setError] = useState<string | null>(null)

  const reset = useCallback(() => {
    setStatus('idle')
    setError(null)
  }, [])

  const fail = useCallback(
    (message: string) => {
      setStatus('error')
      setError(message)
      onError?.()
    },
    [onError],
  )

  const run = useCallback(
    async (action: () => Promise<Document>, fallback: string) => {
      setStatus('uploading')
      setError(null)
      try {
        const document = await action()
        setStatus('success')
        onSuccess?.(document)
      } catch (err) {
        fail(errorMessage(err, fallback))
      }
    },
    [onSuccess, fail],
  )

  const submitPdf = useCallback(
    async (file: File) => {
      if (file.type !== 'application/pdf') {
        fail('Only PDF files are supported.')
        return
      }
      if (file.size > MAX_PDF_BYTES) {
        fail('PDF must be 10 MB or smaller.')
        return
      }
      await run(() => uploadPdf(file), 'Failed to upload PDF.')
    },
    [run, fail],
  )

  const submitUrl = useCallback(
    async (url: string) => {
      const trimmed = url.trim()
      if (!isValidUrl(trimmed)) {
        fail('Enter a valid http(s) URL.')
        return
      }
      await run(() => ingestUrl(trimmed), 'Failed to ingest URL.')
    },
    [run, fail],
  )

  const submitNote = useCallback(
    async (content: string, tags: string[]) => {
      const trimmed = content.trim()
      if (trimmed.length === 0) {
        fail('Note cannot be empty.')
        return
      }
      await run(() => addNote(trimmed, tags), 'Failed to save note.')
    },
    [run, fail],
  )

  return { status, error, submitPdf, submitUrl, submitNote, reset }
}
