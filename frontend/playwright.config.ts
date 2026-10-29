import { defineConfig } from "@playwright/test";

const baseURL = "http://127.0.0.1:32177";

export default defineConfig({
  testDir: "./tests",
  use: {
    baseURL,
    browserName: "chromium",
    trace: "retain-on-failure",
  },
  webServer: {
    command: "node ./scripts/playwright-server.mjs",
    url: `${baseURL}/consultant`,
    env: { NEXT_PUBLIC_API_BASE_URL: baseURL },
    reuseExistingServer: false,
    timeout: 120_000,
  },
});
