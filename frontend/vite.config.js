import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 9939,
    proxy: {
      '/api': {
        target: 'http://localhost:9940',
        changeOrigin: true
      }
    }
  }
})
