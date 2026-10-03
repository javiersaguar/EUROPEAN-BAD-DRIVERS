import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'production-policy',
      apply: 'build',
      transformIndexHtml() {
        return [
          {
            tag: 'meta',
            attrs: {
              'http-equiv': 'Content-Security-Policy',
              content:
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'",
            },
            injectTo: 'head-prepend',
          },
        ]
      },
    },
  ],
  base: process.env.PAGES_BASE || '/',
  build: {
    chunkSizeWarningLimit: 800,
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'charts', test: /node_modules\/(recharts|d3-|victory)/ },
            { name: 'react', test: /node_modules\/(react|react-dom|scheduler)/ },
          ],
        },
      },
    },
  },
})
