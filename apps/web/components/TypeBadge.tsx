import type { DocumentType } from '@/types'

interface TypeBadgeProps {
  type: DocumentType
}

const STYLES: Record<DocumentType, { className: string; label: string }> = {
  pdf: {
    className: 'bg-primary-container text-on-primary-container',
    label: 'PDF',
  },
  url: {
    className: 'bg-secondary-container text-on-secondary-container',
    label: 'URL',
  },
  note: {
    className: 'bg-surface-variant text-on-surface-variant',
    label: 'Note',
  },
}

/** Assist-chip badge indicating a document's source type. */
export function TypeBadge({ type }: TypeBadgeProps) {
  const { className, label } = STYLES[type]
  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium ${className}`}
    >
      {label}
    </span>
  )
}
