/**
 * Demo seed script.
 *
 * Populates a running MiniGlean instance with the sample documents in
 * demo/documents/ so the app is ready for a walkthrough. Idempotent: it lists
 * existing documents first and skips anything already present, so it is safe to
 * run multiple times.
 *
 * Usage:
 *   NEXT_PUBLIC_API_URL=http://localhost:8000 npx tsx demo/seed.ts
 *
 * Requires Node 20+ (global fetch / FormData / Blob).
 */

import { readFile } from 'node:fs/promises'
import { basename, join } from 'node:path'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const DOCS_DIR = join(import.meta.dirname, 'documents')

const PDF_FILES = ['rental-contract.pdf', 'fastapi-notes.pdf']
const NOTE_FILE = 'meeting-notes.txt'
const NOTE_TAGS = ['meeting', 'action-items']

interface Document {
  id: string
  filename: string
  doc_type: string
}

/** Replicates the backend's note-filename derivation for idempotency. */
function noteFilename(content: string): string {
  const text = content.trim()
  return text.length > 50 ? `${text.slice(0, 50)}...` : text
}

async function listDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_URL}/documents`)
  if (!res.ok) {
    throw new Error(`Failed to list documents: ${res.status} ${res.statusText}`)
  }
  return (await res.json()) as Document[]
}

async function uploadPdf(filePath: string): Promise<void> {
  const buffer = await readFile(filePath)
  const form = new FormData()
  form.append(
    'file',
    new Blob([buffer], { type: 'application/pdf' }),
    basename(filePath),
  )
  const res = await fetch(`${API_URL}/documents/upload/pdf`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`Upload failed for ${basename(filePath)}: ${res.status} ${detail}`)
  }
}

async function addNote(content: string, tags: string[]): Promise<void> {
  const res = await fetch(`${API_URL}/documents/note`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, tags }),
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`Note creation failed: ${res.status} ${detail}`)
  }
}

async function main(): Promise<void> {
  console.log(`Seeding MiniGlean at ${API_URL}`)

  const existing = await listDocuments()
  const existingNames = new Set(existing.map((doc) => doc.filename))

  for (const file of PDF_FILES) {
    if (existingNames.has(file)) {
      console.log(`• Skipping ${file} (already present)`)
      continue
    }
    console.log(`• Uploading ${file}`)
    await uploadPdf(join(DOCS_DIR, file))
  }

  const noteContent = await readFile(join(DOCS_DIR, NOTE_FILE), 'utf8')
  const derivedName = noteFilename(noteContent)
  if (existingNames.has(derivedName)) {
    console.log(`• Skipping ${NOTE_FILE} (already present)`)
  } else {
    console.log(`• Adding note from ${NOTE_FILE}`)
    await addNote(noteContent, NOTE_TAGS)
  }

  console.log('Done. Knowledge base is seeded.')
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err)
  process.exit(1)
})
