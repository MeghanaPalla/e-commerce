import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// in dev, requests to /api go to the Flask server
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://127.0.0.1:5000' },
  },
})
