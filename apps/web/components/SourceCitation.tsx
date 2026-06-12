'use client'

import { useState } from 'react'
import { typography } from '@/lib/theme'
import type { SourceCitation as SourceCitationType } from '@/types'

interface SourceCitationProps {
  citation: SourceCitationType
}

/** Expandable assist chip showing a cited source's filename and excerpt. */
export function SourceCitation({ citation }: SourceCitationProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="flex flex-col gap-1">
      <button
        type="button"
        aria-expanded={expanded}
        onClick={() => setExpanded((value) => !value)}
        className={[
          typography.label.large,
          'inline-flex max-w-full items-center gap-1.5 rounded-md border border-outline-variant',
          'px-3 py-1 text-on-surface-variant transition-colors hover:bg-surface-variant',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
        ].join(' ')}
      >
        <span aria-hidden="true">📄</span>
        <span className="truncate">{citation.filename}</span>
      </button>

      {expanded ? (
        <p
          className={`${typography.body.small} rounded-md bg-surface-variant px-3 py-2 text-on-surface-variant`}
        >
          {citation.excerpt}
        </p>
      ) : null}
    </div>
  )
}
