import { defineConfig } from "vite";

export default defineConfig({
  root: "./",
  base: "./",
  build: {
    outDir: "dist",
    assetsDir: "assets",
    sourcemap: false,
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    open: true,
  },
  test: {
    environment: "jsdom",
    globals: true,
    exclude: ["tests-e2e/**", "node_modules/**"],
  },
});
