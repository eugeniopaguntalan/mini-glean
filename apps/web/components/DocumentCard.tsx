import { TypeBadge } from '@/components/TypeBadge'
import { typography } from '@/lib/theme'
import type { Document } from '@/types'

interface DocumentCardProps {
  document: Document
  onDelete: (id: string) => void
}

function formatDate(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/** Elevated card summarizing a single document in the library. */
export function DocumentCard({ document, onDelete }: DocumentCardProps) {
  const chunkLabel = `${document.chunk_count} ${
    document.chunk_count === 1 ? 'chunk' : 'chunks'
  }`
  const date = formatDate(document.created_at)

  return (
    <article className="flex flex-col gap-3 rounded-xl bg-surface p-4 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <h3
          className={`${typography.title.medium} break-words text-on-surface`}
          title={document.filename}
        >
          {document.filename}
        </h3>
        <TypeBadge type={document.type} />
      </div>

      <p className={`${typography.body.medium} text-on-surface-variant`}>
        {chunkLabel}
        {date ? ` · ${date}` : ''}
      </p>

      {document.tags.length > 0 ? (
        <ul className="flex flex-wrap gap-1.5">
          {document.tags.map((tag) => (
            <li
              key={tag}
              className="rounded-md bg-surface-variant px-2 py-0.5 text-[11px] font-medium text-on-surface-variant"
            >
              {tag}
            </li>
          ))}
        </ul>
      ) : null}

      <div className="mt-auto flex justify-end pt-1">
        <button
          type="button"
          onClick={() => onDelete(document.id)}
          aria-label={`Delete ${document.filename}`}
          className={`${typography.label.large} rounded-full px-4 py-1.5 text-error transition-colors hover:bg-error/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-error`}
        >
          Delete
        </button>
      </div>
    </article>
  )
}
