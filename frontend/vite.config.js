import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// When running inside Docker, proxy targets use host.docker.internal.
// When running on the host directly, targets fall back to localhost.
const HOST = process.env.DOCKER_HOST ?? 'localhost'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    // Dev server sits behind Caddy/Cloudflare tunnel; the Host header arriving
    // here is whatever the upstream sets. Allow public host + upstream alias.
    allowedHosts: [
      '.yogaman.club',
      'host.docker.internal',
      'localhost',
      '127.0.0.1',
    ],
    proxy: {
      '/api/v1': {
        target: `http://${HOST}:19090`,
        changeOrigin: true,
      },
      // Both /search and /chat are served by the single FastAPI app.
      // Docker: 5001 (search) / 5002 (chat). Local dev: both on 8000.
      '/search': {
        target: `http://${HOST}:${process.env.SEARCH_PORT ?? 8000}`,
        changeOrigin: true,
      },
      '/chat': {
        target: `http://${HOST}:${process.env.CHAT_PORT ?? 8000}`,
        changeOrigin: true,
      },
      // elbee Studio (operator chatbot) — same FastAPI app as /chat.
      '/studio': {
        target: `http://${HOST}:${process.env.CHAT_PORT ?? 8000}`,
        changeOrigin: true,
      },
    },
  },
})
