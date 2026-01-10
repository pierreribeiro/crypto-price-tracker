import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // Code splitting configuration
  build: {
    rollupOptions: {
      output: {
        // Manual chunks for better code splitting
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom'],
          // Chart library separate chunk (large dependency)
          // 'lightweight-charts': ['lightweight-charts'], // Uncomment when installed
        },
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000, // 1MB
    // Source maps for debugging
    sourcemap: true,
  },

  // Development server configuration
  server: {
    port: 5173,
    strictPort: false,
    host: true,
    open: false,
  },

  // Environment variable prefix (allows VITE_ prefixed vars)
  envPrefix: 'VITE_',

  // Path resolution
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
