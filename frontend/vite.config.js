import process from 'node:process'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages serves the site from /lexflow/ (set by the deploy workflow); locally it's "/".
  base: process.env.PAGES_BASE || '/',
})
