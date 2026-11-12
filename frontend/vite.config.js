import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/resume': 'http://127.0.0.1:8000',
      '/jobs': 'http://127.0.0.1:8000',
      '/apply': 'http://127.0.0.1:8000',
      '/screenshots': 'http://127.0.0.1:8000',
    }
  }
})
