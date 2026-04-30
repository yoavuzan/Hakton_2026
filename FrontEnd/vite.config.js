import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  server: {
    allowedHosts: ['hakton-2026-7ptp.onrender.com'],
    host: true,
    port: 5173
  }
})
