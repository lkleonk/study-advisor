import { expect, test } from "@playwright/test";

import { CURRENT_WELCOME_VERSION } from "../src/app/consultant/components/storage";

test("a restored plan separates Wahlbereich and shows prior-credit uncertainty", async ({ page }) => {
  await page.addInitScript((welcomeVersion) => {
    localStorage.setItem("fu-consultant-welcome-version", welcomeVersion);
    localStorage.setItem("fu-consultant-degree", "msc_informatik");
    sessionStorage.setItem("fu-consultant-session-id", "stored-session");
    const defaults = {
      lp: 10,
      area: "technical",
      is_ungraded: false,
      is_bachelor_module: false,
      is_scientific_work: false,
      is_software_project: false,
      is_wahlbereich: false,
    };
    sessionStorage.setItem("fu-consultant-chat-messages", JSON.stringify([{
      id: "stored-upload",
      role: "assistant",
      content: "A partial plan was extracted.",
      parsedStudyPlan: {
        specialization_area: "technical",
        modules: [
          { ...defaults, name: "Previously credited module", counted_in_bachelor: true },
          // Old saved plans have neither of the new prior-credit fields.
          { ...defaults, name: "Additional Bachelor-level module", is_wahlbereich: true, is_bachelor_module: true },
        ],
      },
      ruleCheckResult: null,
    }]));
  }, CURRENT_WELCOME_VERSION);

  await page.route("**/api/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/api/degrees") {
      await route.fulfill({ json: [{ id: "msc_informatik", display_name: "M.Sc. Informatik", regulation: "SPO 2014", plan_validation_enabled: true }] });
    } else if (path === "/api/usage") {
      await route.fulfill({ json: {
        limit: 60, used: 0, remaining: 60, reset_at: "2099-01-01T00:00:00Z",
        service: { limit: 150, used: 0, remaining: 150 },
        session_inactivity_ttl_seconds: 172800, diagnostic_tracing_enabled: false, quota_scope: "client_ip",
      } });
    } else {
      await route.fulfill({ status: 404, json: { detail: `Unexpected API request: ${path}` } });
    }
  });

  await page.goto("/consultant");
  await page.getByRole("tab", { name: "Study Plan", exact: true }).click();
  await expect(page.getByText("Informatik: 10 LP", { exact: true })).toBeVisible();
  await expect(page.getByText("Anwendungsbereich: 0 LP", { exact: true })).toBeVisible();
  await expect(page.getByText("Wahlbereich: 10 LP", { exact: true })).toBeVisible();
  await expect(page.getByText("Already counted in Bachelor", { exact: true })).toBeVisible();
  await expect(page.getByText("Prior credit use unconfirmed", { exact: true })).toBeVisible();
  await expect(page.getByText("Additional Bachelor-level module", { exact: true })).toHaveCount(1);
});
