/**
 * Unit tests for the API client (`lib/api.ts`).
 *
 * `fetch` is stubbed for every test so no real network calls are made. These
 * cover the happy paths, error normalization (`toApiError`), the
 * network-failure fallback (`networkError`), and the SSE parsing in
 * `streamChat`.
 */

import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  addNote,
  chat,
  deleteDocument,
  ingestUrl,
  listDocuments,
  streamChat,
  uploadPdf,
} from '@/lib/api'
import type { ChatResponse, Document } from '@/types'

const sampleDoc: Document = {
  id: 'doc-1',
  filename: 'guide.pdf',
  type: 'pdf',
  tags: ['ai'],
  chunk_count: 3,
  created_at: '2026-01-01T00:00:00Z',
}

/** Build a mock `Response`-like object with the given JSON body. */
function jsonResponse(body: unknown, init?: { ok?: boolean; status?: number }) {
  return {
    ok: init?.ok ?? true,
    status: init?.status ?? 200,
    statusText: 'OK',
    json: async () => body,
    text: async () => JSON.stringify(body),
  } as unknown as Response
}

/** Build a mock error `Response` with a raw text body. */
function errorResponse(
  text: string,
  status = 500,
  statusText = 'Internal Server Error',
) {
  return {
    ok: false,
    status,
    statusText,
    json: async () => JSON.parse(text),
    text: async () => text,
  } as unknown as Response
}

/** Build a streaming `Response` whose body yields the given SSE text. */
function streamResponse(sse: string, init?: { ok?: boolean; status?: number }) {
  const bytes = new TextEncoder().encode(sse)
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(bytes)
      controller.close()
    },
  })
  return {
    ok: init?.ok ?? true,
    status: init?.status ?? 200,
    statusText: 'OK',
    body,
    text: async () => sse,
    json: async () => JSON.parse(sse),
  } as unknown as Response
}

function mockFetch(impl: typeof fetch) {
  vi.stubGlobal('fetch', vi.fn(impl))
  return globalThis.fetch as unknown as ReturnType<typeof vi.fn>
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('listDocuments', () => {
  it('returns the parsed document list', async () => {
    mockFetch(async () => jsonResponse([sampleDoc]))
    const docs = await listDocuments()
    expect(docs).toEqual([sampleDoc])
  })

  it('requests GET /documents', async () => {
    const fetchMock = mockFetch(async () => jsonResponse([]))
    await listDocuments()
    const [url, options] = fetchMock.mock.calls[0]
    expect(String(url)).toContain('/documents')
    expect(options.method).toBe('GET')
  })
})

describe('error normalization', () => {
  it('extracts `detail` from a JSON error body', async () => {
    mockFetch(async () =>
      errorResponse(JSON.stringify({ detail: 'Document not found' }), 404),
    )
    await expect(listDocuments()).rejects.toMatchObject({
      detail: 'Document not found',
      status: 404,
    })
  })

  it('falls back to the raw body when it is not JSON', async () => {
    mockFetch(async () => errorResponse('Bad gateway', 502, 'Bad Gateway'))
    await expect(listDocuments()).rejects.toMatchObject({
      detail: 'Bad gateway',
      status: 502,
    })
  })
})

describe('network failures', () => {
  it('reports an unreachable server when fetch throws', async () => {
    mockFetch(async () => {
      throw new TypeError('Failed to fetch')
    })
    await expect(listDocuments()).rejects.toMatchObject({
      detail: 'Cannot reach the server. Please try again.',
      status: 0,
    })
  })

  it('reports no internet connection when navigator is offline', async () => {
    vi.stubGlobal('navigator', { onLine: false })
    mockFetch(async () => {
      throw new TypeError('Failed to fetch')
    })
    await expect(listDocuments()).rejects.toMatchObject({
      detail: 'No internet connection.',
      status: 0,
    })
  })
})

describe('uploadPdf', () => {
  it('posts multipart form data and returns the document', async () => {
    const fetchMock = mockFetch(async () => jsonResponse(sampleDoc))
    const file = new File(['%PDF-1.4'], 'guide.pdf', { type: 'application/pdf' })

    const result = await uploadPdf(file)

    expect(result).toEqual(sampleDoc)
    const [url, options] = fetchMock.mock.calls[0]
    expect(String(url)).toContain('/documents/upload/pdf')
    expect(options.method).toBe('POST')
    expect(options.body).toBeInstanceOf(FormData)
  })
})

describe('ingestUrl and addNote', () => {
  it('sends the url in the request body', async () => {
    const fetchMock = mockFetch(async () => jsonResponse(sampleDoc))
    await ingestUrl('https://example.com')
    const [, options] = fetchMock.mock.calls[0]
    expect(JSON.parse(options.body as string)).toEqual({
      url: 'https://example.com',
    })
  })

  it('sends content and default empty tags for a note', async () => {
    const fetchMock = mockFetch(async () => jsonResponse(sampleDoc))
    await addNote('remember this')
    const [, options] = fetchMock.mock.calls[0]
    expect(JSON.parse(options.body as string)).toEqual({
      content: 'remember this',
      tags: [],
    })
  })
})

describe('deleteDocument', () => {
  it('resolves on a 204 with no body', async () => {
    mockFetch(
      async () =>
        ({ ok: true, status: 204, statusText: 'No Content' }) as Response,
    )
    await expect(deleteDocument('doc-1')).resolves.toBeUndefined()
  })

  it('throws a normalized error on failure', async () => {
    mockFetch(async () =>
      errorResponse(JSON.stringify({ detail: 'gone' }), 404),
    )
    await expect(deleteDocument('doc-1')).rejects.toMatchObject({ status: 404 })
  })
})

describe('chat', () => {
  it('returns the chat response', async () => {
    const response: ChatResponse = {
      id: 'msg-1',
      content: 'Here is the answer.',
      sources: [],
      created_at: '2026-01-01T00:00:00Z',
      session_id: 'session-1',
    }
    const fetchMock = mockFetch(async () => jsonResponse(response))

    const result = await chat('What is this?', 'session-1')

    expect(result).toEqual(response)
    const [, options] = fetchMock.mock.calls[0]
    expect(JSON.parse(options.body as string)).toEqual({
      question: 'What is this?',
      session_id: 'session-1',
    })
  })
})

describe('streamChat', () => {
  it('yields each token and the sources payload, stopping at [DONE]', async () => {
    const sse =
      'data: Hello\n\n' +
      'data:  world\n\n' +
      'data: [SOURCES]{"sources":[]}\n\n' +
      'data: [DONE]\n\n'
    mockFetch(async () => streamResponse(sse))

    const chunks: string[] = []
    for await (const chunk of streamChat('q', 'session-1')) {
      chunks.push(chunk)
    }

    expect(chunks).toEqual(['Hello', ' world', '[SOURCES]{"sources":[]}'])
  })

  it('throws an ApiError when the stream reports [ERROR]', async () => {
    const sse = 'data: partial\n\ndata: [ERROR]rate limited\n\n'
    mockFetch(async () => streamResponse(sse))

    const iterate = async () => {
      const out: string[] = []
      for await (const chunk of streamChat('q', 'session-1')) {
        out.push(chunk)
      }
      return out
    }

    await expect(iterate()).rejects.toMatchObject({
      detail: 'rate limited',
      status: 0,
    })
  })

  it('throws a normalized error when the request is not ok', async () => {
    mockFetch(async () =>
      errorResponse(JSON.stringify({ detail: 'server down' }), 503),
    )
    const iterate = async () => {
      for await (const _ of streamChat('q', 'session-1')) {
        void _
      }
    }
    await expect(iterate()).rejects.toMatchObject({ status: 503 })
  })
})
