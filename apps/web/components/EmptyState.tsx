import type { ReactNode } from 'react'
import { typography } from '@/lib/theme'

interface EmptyStateProps {
  title: string
  description: string
  icon?: ReactNode
}

/** Centered placeholder shown when a view has no content yet. */
export function EmptyState({ title, description, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
      {icon ? (
        <div className="text-on-surface-variant" aria-hidden="true">
          {icon}
        </div>
      ) : null}
      <h2 className={`${typography.title.large} text-on-surface`}>{title}</h2>
      <p className={`${typography.body.medium} max-w-sm text-on-surface-variant`}>
        {description}
      </p>
    </div>
  )
}
