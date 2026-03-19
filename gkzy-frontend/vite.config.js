import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
<<<<<<< HEAD
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    open: true
  }
})
=======

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
})
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862
