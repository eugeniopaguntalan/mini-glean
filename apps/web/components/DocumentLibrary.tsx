import { DocumentCard } from '@/components/DocumentCard'
import { EmptyState } from '@/components/EmptyState'
import { ErrorBanner } from '@/components/ErrorBanner'
import type { Document } from '@/types'

interface DocumentLibraryProps {
  documents: Document[]
  loading: boolean
  error: string | null
  onRetry: () => void
  onDelete: (id: string) => void
}

const SKELETON_COUNT = 6

function SkeletonGrid() {
  return (
    <div
      className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      aria-hidden="true"
    >
      {Array.from({ length: SKELETON_COUNT }).map((_, index) => (
        <div
          key={index}
          className="h-32 animate-pulse rounded-xl bg-surface-variant"
        />
      ))}
    </div>
  )
}

/** Renders the document grid with loading, empty, and error states. */
export function DocumentLibrary({
  documents,
  loading,
  error,
  onRetry,
  onDelete,
}: DocumentLibraryProps) {
  if (loading) {
    return <SkeletonGrid />
  }

  if (error) {
    return <ErrorBanner message={error} onRetry={onRetry} />
  }

  if (documents.length === 0) {
    return (
      <EmptyState
        title="No documents yet"
        description="Upload a PDF, paste a URL, or write a note to get started."
      />
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
