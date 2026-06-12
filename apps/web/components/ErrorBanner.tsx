import { typography } from '@/lib/theme'

interface ErrorBannerProps {
  message: string
  onRetry?: () => void
}

/** Red-tinted alert card with an optional retry action. */
export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className="flex items-center justify-between gap-4 rounded-xl border border-error/30 bg-error/5 px-4 py-3"
    >
      <p className={`${typography.body.medium} text-error`}>{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className={`${typography.label.large} shrink-0 rounded-full px-4 py-1.5 text-error transition-colors hover:bg-error/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-error`}
        >
          Retry
        </button>
      ) : null}
    </div>
  )
}
