'use client'

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
  type KeyboardEvent,
} from 'react'
import { ErrorBanner } from '@/components/ErrorBanner'
import { useUpload, type UploadMode } from '@/hooks/useUpload'
import { filledButton, typography } from '@/lib/theme'

interface UploadPanelProps {
  onUploaded: () => void
}

const TABS: { id: UploadMode; label: string }[] = [
  { id: 'pdf', label: 'PDF' },
  { id: 'url', label: 'URL' },
  { id: 'note', label: 'Note' },
]

function parseTags(raw: string): string[] {
  return raw
    .split(',')
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0)
}

/** Outlined card with PDF / URL / Note tabs for ingesting new documents. */
export function UploadPanel({ onUploaded }: UploadPanelProps) {
  const [tab, setTab] = useState<UploadMode>('pdf')
  const [file, setFile] = useState<File | null>(null)
  const [url, setUrl] = useState('')
  const [note, setNote] = useState('')
  const [tags, setTags] = useState('')
  const [dragging, setDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSuccess = useCallback(() => {
    setFile(null)
    setUrl('')
    setNote('')
    setTags('')
    if (fileInputRef.current) fileInputRef.current.value = ''
    onUploaded()
  }, [onUploaded])

  // Clear the chosen file (and the native input) when an upload fails so the
  // user can re-select rather than being stuck with a stale selection.
  const handleError = useCallback(() => {
    setFile(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }, [])

  const { status, error, submitPdf, submitUrl, submitNote, reset } = useUpload({
    onSuccess: handleSuccess,
    onError: handleError,
  })

  const uploading = status === 'uploading'

  // Auto-dismiss the success message after a short delay.
  useEffect(() => {
    if (status !== 'success') return
    const timer = setTimeout(reset, 2500)
    return () => clearTimeout(timer)
  }, [status, reset])

  const switchTab = useCallback(
    (next: UploadMode) => {
      setTab(next)
      reset()
    },
    [reset],
  )

  const handleFiles = useCallback((files: FileList | null) => {
    const selected = files?.[0]
    if (selected) setFile(selected)
  }, [])

  const handleDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault()
      setDragging(false)
      handleFiles(event.dataTransfer.files)
    },
    [handleFiles],
  )

  const handleFileChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      handleFiles(event.target.files)
    },
    [handleFiles],
  )

  const openFilePicker = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const handleDropZoneKeyDown = useCallback(
    (event: KeyboardEvent<HTMLDivElement>) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        openFilePicker()
      }
    },
    [openFilePicker],
  )

  const handleSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault()
      if (tab === 'pdf') {
        if (file) void submitPdf(file)
        return
      }
      if (tab === 'url') {
        void submitUrl(url)
        return
      }
      void submitNote(note, parseTags(tags))
    },
    [tab, file, url, note, tags, submitPdf, submitUrl, submitNote],
  )

  return (
    <section className="rounded-xl border border-outline-variant bg-surface p-5">
      <h2 className={`${typography.title.large} mb-4 text-on-surface`}>
        Add a document
      </h2>

      <div role="tablist" aria-label="Upload type" className="mb-5 flex gap-2">
        {TABS.map(({ id, label }) => {
          const active = tab === id
          return (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => switchTab(id)}
              className={[
                typography.label.large,
                'rounded-full px-4 py-1.5 transition-colors',
                active
                  ? 'bg-secondary-container text-on-secondary-container'
                  : 'text-on-surface-variant hover:bg-surface-variant',
              ].join(' ')}
            >
              {label}
            </button>
          )
        })}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {tab === 'pdf' ? (
          <>
            <div
              role="button"
              tabIndex={0}
              aria-label="Upload PDF"
              onClick={openFilePicker}
              onKeyDown={handleDropZoneKeyDown}
              onDragOver={(event) => {
                event.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              className={[
                'flex cursor-pointer flex-col items-center justify-center gap-2',
                'rounded-xl border-2 border-dashed px-4 py-10 text-center transition-colors',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
                dragging
                  ? 'border-primary bg-primary/8'
                  : 'border-outline-variant hover:border-primary',
              ].join(' ')}
            >
              <p className={`${typography.body.large} text-on-surface`}>
                {file ? file.name : 'Drag & drop a PDF here'}
              </p>
              <p className={`${typography.body.medium} text-on-surface-variant`}>
                or click to browse · max 10 MB
              </p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            <button
              type="submit"
              disabled={uploading || !file}
              className={filledButton}
            >
              {uploading ? 'Uploading…' : 'Upload PDF'}
            </button>
          </>
        ) : null}

        {tab === 'url' ? (
          <>
            <input
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://example.com/article"
              aria-label="Document URL"
              className={`${typography.body.large} rounded-md border border-outline-variant bg-surface px-4 py-2.5 text-on-surface placeholder:text-on-surface-variant focus:border-primary focus:outline-none`}
            />
            <button
              type="submit"
              disabled={uploading || url.trim().length === 0}
              className={filledButton}
            >
              {uploading ? 'Ingesting…' : 'Ingest URL'}
            </button>
          </>
        ) : null}

        {tab === 'note' ? (
          <>
            <textarea
              value={note}
              onChange={(event) => setNote(event.target.value)}
              rows={5}
              placeholder="Write a note to remember…"
              aria-label="Note content"
              className={`${typography.body.large} resize-none rounded-md border border-outline-variant bg-surface px-4 py-2.5 text-on-surface placeholder:text-on-surface-variant focus:border-primary focus:outline-none`}
            />
            <input
              type="text"
              value={tags}
              onChange={(event) => setTags(event.target.value)}
              placeholder="Tags (comma separated, optional)"
              aria-label="Note tags"
              className={`${typography.body.medium} rounded-md border border-outline-variant bg-surface px-4 py-2 text-on-surface placeholder:text-on-surface-variant focus:border-primary focus:outline-none`}
            />
            <button
              type="submit"
              disabled={uploading || note.trim().length === 0}
              className={filledButton}
            >
              {uploading ? 'Saving…' : 'Save note'}
            </button>
          </>
        ) : null}

        {status === 'success' ? (
          <p
            role="status"
            className={`${typography.body.medium} text-primary`}
          >
            Added to your library.
          </p>
        ) : null}

        {status === 'error' && error ? <ErrorBanner message={error} /> : null}
      </form>
    </section>
  )
}
