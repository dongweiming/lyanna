import { fileURLToPath, URL } from 'url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        }
    },
    build: {
        rollupOptions: {
            output: {
                entryFileNames: '[name].js',
                chunkFileNames: '[name].js',
                assetFileNames: '[name].[ext]'
            }
        }
    },
    server: {
        proxy: {
            ...['/api', '/static', '/j'].reduce(
                (acc, ctx) => ({
                    ...acc,
                    [ctx]: {
                        target: 'http://127.0.0.1:8000',
                        changeOrigin: true
                    },
                }),
                {}
            ),
        }
    },
})
