import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  server: {
    port: 3001,
    host: 'localhost',
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    target: 'es2015',
    rollupOptions: {
      external: [],
      output: {
        manualChunks: undefined
      }
    }
  },
  esbuild: {
    // 跳过类型检查以快速启动
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  }
})