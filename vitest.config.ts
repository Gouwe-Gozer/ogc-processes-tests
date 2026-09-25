import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const root = fileURLToPath(new URL(".", import.meta.url));
// Set by the Python launcher for one child process; no installed package changes.
const local = process.env.OAP_TEST_CLIENT_DIR;
const packageDir = local ?? resolve(root, "node_modules/@breinstein/oap-client");
const manifest = JSON.parse(readFileSync(resolve(packageDir, "package.json"), "utf8"));
console.info(`Client under test: ${local ? "LOCAL build" : "installed npm package"} ${manifest.version} (${packageDir})`);

export default defineConfig({
  resolve: {
    alias: local ? [{
      find: /^@breinstein\/oap-client$/,
      replacement: resolve(packageDir, manifest.exports["."].default),
    }] : [],
  },
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
    setupFiles: ["./tests/setup.ts"],
  },
});
