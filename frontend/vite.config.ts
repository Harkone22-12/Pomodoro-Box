import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development, /api and Socket.IO are proxied to the backend on :3000,
// so the browser only ever talks to the Vite origin.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:3000",
      "/socket.io": { target: "http://localhost:3000", ws: true },
    },
  },
});
