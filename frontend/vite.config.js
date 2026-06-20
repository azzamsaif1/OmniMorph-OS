import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

function suppressConnRefused(proxy) {
  const originalEmit = proxy.emit.bind(proxy);
  proxy.emit = function (event, ...args) {
    if (event === "error" && args[0] && args[0].code === "ECONNREFUSED") {
      const res = args[2];
      if (res && typeof res.writeHead === "function") {
        if (!res.headersSent) {
          res.writeHead(503, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Backend unavailable" }));
        }
      } else if (res && typeof res.destroy === "function") {
        res.destroy();
      }
      return true;
    }
    return originalEmit(event, ...args);
  };
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        configure: suppressConnRefused,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
        configure: suppressConnRefused,
      },
    },
  },
});
