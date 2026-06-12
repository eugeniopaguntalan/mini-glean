'use client'

import { DocumentLibrary } from '@/components/DocumentLibrary'
import { UploadPanel } from '@/components/UploadPanel'
import { useDocuments } from '@/hooks/useDocuments'
import { typography } from '@/lib/theme'

export default function Home() {
  const { documents, loading, error, refetch, deleteDocument } = useDocuments()

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">
      <header className="mb-8">
        <h1 className={`${typography.headline.large} text-on-surface`}>
          Your knowledge base
        </h1>
        <p className={`${typography.body.large} mt-1 text-on-surface-variant`}>
          Upload documents and search across everything you know.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <UploadPanel onUploaded={refetch} />
        </div>
        <div className="lg:col-span-2">
          <DocumentLibrary
            documents={documents}
            loading={loading}
            error={error}
            onRetry={refetch}
            onDelete={deleteDocument}
          />
        </div>
      </div>
    </main>
  )
}

