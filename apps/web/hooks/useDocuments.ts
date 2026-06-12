'use client'

import { useCallback, useEffect, useState } from 'react'
import { deleteDocument as apiDeleteDocument, listDocuments } from '@/lib/api'
import type { ApiError, Document } from '@/types'

interface UseDocumentsResult {
  documents: Document[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  deleteDocument: (id: string) => Promise<void>
}

function errorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'detail' in err) {
    return (err as ApiError).detail
  }
  return 'Something went wrong while loading documents.'
}

/**
 * Loads and manages the document library.
 *
 * Fetches on mount, exposes `refetch` for the upload panel to call after a
 * successful ingest, and performs an optimistic `deleteDocument` that rolls
 * back if the request fails.
 */
export function useDocuments(): UseDocumentsResult {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial load on mount. State is only updated after the await resolves, so
  // no synchronous setState happens inside the effect body.
  useEffect(() => {
    let active = true
    void (async () => {
      try {
        const docs = await listDocuments()
        if (active) setDocuments(docs)
      } catch (err) {
        if (active) setError(errorMessage(err))
      } finally {
        if (active) setLoading(false)
      }
    })()
    return () => {
      active = false
    }
  }, [])

  const deleteDocument = useCallback(
    async (id: string) => {
      const previous = documents
      // Optimistically remove from the list for instant feedback.
      setDocuments((docs) => docs.filter((doc) => doc.id !== id))
      setError(null)
      try {
        await apiDeleteDocument(id)
      } catch (err) {
        // Roll back on failure.
        setDocuments(previous)
        setError(errorMessage(err))
      }
    },
    [documents],
  )

  return { documents, loading, error, refetch, deleteDocument }
}
