import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import WindiCSS from 'vite-plugin-windicss';

export default defineConfig(({ mode }) => {
  // Correctly load environment variables
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [react(), WindiCSS()],
    server: {
      host: '0.0.0.0',  // This makes the server accessible on all network interfaces
      port: 5173,       // Port the frontend will run on
      proxy: {
        '/api': {
          target: env.VITE_API_URL || "http://127.0.0.1:5000", // Ensure your backend API is correctly proxied
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, ''), // Remove /api prefix when forwarding to backend
        },
      },
    },
  };
});
