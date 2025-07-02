import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/api/v1': {
        // target: 'http://8.148.71.20:8000',
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        // 不需要重写路径，Django 已经配置了 /api/v1 前缀
        // rewrite: (path) => path.replace(/^\/api\/v1/, '/api/v1')
      }
    }
  },
})
