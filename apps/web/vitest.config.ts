import { resolve } from 'node:path'
import { defineConfig } from 'vitest/config'

/**
 * Vitest configuration for the web app's unit tests.
 *
 * Tests run in a Node environment (the API client only needs `fetch`, not the
 * DOM). The `@/` alias mirrors `tsconfig.json` so test imports match app code.
 */
export default defineConfig({
  test: {
    environment: 'node',
    include: ['**/*.test.ts', '**/*.test.tsx'],
    exclude: ['node_modules', '.next'],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, '.'),
    },
  },
})
