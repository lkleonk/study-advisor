import { expect, test, type Page } from "@playwright/test";

import { CURRENT_WELCOME_VERSION } from "../src/app/consultant/components/storage";
import type {
  ProgramRuleItem,
  ProgramRuleSection,
  ProgramRulesCatalogue,
} from "../src/types/api";

function item(
  label: string,
  text: string,
  credits: number | null = null,
): ProgramRuleItem {
  return {
    label,
    text,
    minimum: credits,
    maximum: credits,
    unit: credits === null ? null : "LP",
  };
}

function section(
  id: string,
  title: string,
  items: ProgramRuleItem[],
): ProgramRuleSection {
  return {
    id,
    title,
    description: `Full guidance about ${title}.`,
    items,
    related_issue_codes: [],
    sources: [
      {
        label: "Official regulation",
        path: "https://example.com/regulation",
        note: "Check the applicable regulation.",
      },
    ],
  };
}

// Deliberately small API fixture: navigation and preservation, not rule validation.
const catalogue: ProgramRulesCatalogue = {
  degree_program: "FU Berlin M.Sc. Informatik",
  regulation: "SPO 2014",
  catalogue_version: "test-catalogue",
  source_note: "The complete source note stays available here.",
  sections: [
    section("overall-structure", "Overall Structure", [
      item("Total degree volume", "120 LP total.", 120),
      item("Taught modules", "90 LP before the thesis.", 90),
      item("Masterarbeit", "30 LP for the thesis.", 30),
    ]),
    section("informatics-area", "1. Informatik (70 LP)", [
      item("Informatik total", "Exclude Wahlbereich from this allocation.", 70),
    ]),
    section("application-area", "2. Anwendungsbereich (10 LP)", [
      item(
        "Application area LP",
        "Scientific subjects outside Informatik.",
        10,
      ),
    ]),
    section("wahlbereich", "3. Wahlbereich (10 LP)", [
      item("Wahlbereich volume", "A separate allocation.", 10),
    ]),
    section("masterarbeit", "4. Masterarbeit (30 LP)", [
      item("Thesis volume", "Contact your supervisor before starting.", 30),
    ]),
    section("wissenschaftliches-arbeiten", "Seminars & projects", [
      item(
        "Module limits",
        "The whole-plan seminar limit includes Wahlbereich.",
      ),
    ]),
    section("bachelor-modules", "Earlier credits", [
      item(
        "Prior use",
        "Credits already counted in a Bachelor cannot count again.",
      ),
      item(
        "Recognition details",
        "Ask for an individual recognition decision.",
      ),
    ]),
    section("exam-registration", "Exam registration", [
      item("Prüfungsanmeldung", "Register separately for the examination."),
    ]),
    section("future-rule", "New programme-specific topic", [
      item("New requirement", "New catalogue topics remain accessible."),
    ]),
  ],
};

async function openRules(page: Page) {
  await page.addInitScript((version) => {
    localStorage.setItem("fu-consultant-welcome-version", version);
    localStorage.setItem("fu-consultant-degree", "msc_informatik");
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: async (text: string) => {
          (window as Window & { copiedRules?: string }).copiedRules = text;
        },
      },
    });
  }, CURRENT_WELCOME_VERSION);
  await page.route("**/api/**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname === "/api/degrees") {
      await route.fulfill({
        json: [
          {
            id: "msc_informatik",
            display_name: "M.Sc. Informatik",
            regulation: "SPO 2014",
            plan_validation_enabled: true,
          },
          {
            id: "bsc_physik",
            display_name: "B.Sc. Physik",
            regulation: "SPO 2024",
            plan_validation_enabled: false,
          },
        ],
      });
    } else if (url.pathname === "/api/program-rules") {
      await route.fulfill({
        json:
          url.searchParams.get("degree") === "bsc_physik"
            ? {
                ...catalogue,
                degree_program: "FU Berlin B.Sc. Physik",
                sections: [
                  section("overall-structure", "Overall Structure", [
                    item("Total degree volume", "180 LP total.", 180),
                    item("Kernfach Physik", "150 LP subject area.", 150),
                    item("ABV", "30 LP ABV.", 30),
                  ]),
                ],
              }
            : catalogue,
      });
    } else if (url.pathname === "/api/usage") {
      await route.fulfill({
        json: {
          limit: 60,
          used: 0,
          remaining: 60,
          reset_at: "2099-01-01T00:00:00Z",
          service: { limit: 150, used: 0, remaining: 150 },
          session_inactivity_ttl_seconds: 172800,
          diagnostic_tracing_enabled: false,
          quota_scope: "client_ip",
        },
      });
    } else {
      await route.fulfill({
        status: 404,
        json: { detail: "Unexpected API request" },
      });
    }
  });
  await page.goto("/consultant");
  await page.getByRole("tab", { name: "Degree Rules", exact: true }).click();
  await expect(
    page.getByRole("region", { name: "Degree at a glance" }),
  ).toBeVisible();
}

test("read the overview, browse topics, search globally, and copy the full rules", async ({
  page,
}) => {
  await openRules(page);
  const overview = page.getByRole("region", { name: "Degree at a glance" });
  await expect(overview.getByRole("button")).toHaveCount(4);
  await expect(overview).toContainText("120 LP total");
  await expect(
    page.getByText("Exclude Wahlbereich from this allocation."),
  ).not.toBeVisible();
  await overview
    .getByRole("button", { name: "70 LP Informatik", exact: true })
    .click();
  await expect(
    page.getByText("Exclude Wahlbereich from this allocation."),
  ).toBeVisible();

  await page
    .getByRole("navigation", { name: "Rule topics" })
    .getByRole("button", { name: /Choosing modules/ })
    .click();
  await page
    .getByRole("button", { name: "Seminars & projects", exact: true })
    .click();
  await expect(
    page.getByText("The whole-plan seminar limit includes Wahlbereich."),
  ).toBeVisible();
  await expect(
    page.getByRole("button", {
      name: "New programme-specific topic",
      exact: true,
    }),
  ).toBeVisible();

  await page
    .getByRole("textbox", { name: "Search all rules" })
    .fill("already counted");
  await expect(
    page.getByText("Credits already counted in a Bachelor cannot count again."),
  ).toBeVisible();
  await expect(
    page.getByText("Ask for an individual recognition decision."),
  ).not.toBeVisible();
  await page
    .getByRole("button", { name: "Copy all rules", exact: true })
    .click();
  const copied = await page.evaluate(
    () => (window as Window & { copiedRules?: string }).copiedRules,
  );
  for (const entry of catalogue.sections) {
    expect(copied).toContain(entry.title);
    for (const rule of entry.items) expect(copied).toContain(rule.text);
  }
  expect(copied).toContain(catalogue.source_note);
  expect(copied).toContain("https://example.com/regulation");

  await page
    .getByRole("textbox", { name: "Search all rules" })
    .fill("prufungsanmeldung");
  await expect(
    page.getByText("Register separately for the examination."),
  ).toBeVisible();
  await page
    .getByRole("textbox", { name: "Search all rules" })
    .fill("no such rule xyz");
  await expect(page.getByText(/No rules match/)).toBeVisible();
  await page.getByRole("button", { name: "Clear search", exact: true }).click();
  await expect(
    page.getByRole("button", {
      name: "New programme-specific topic",
      exact: true,
    }),
  ).toBeVisible();

  await page.getByRole("button", { name: "All topics", exact: true }).click();
  await page.getByRole("button", { name: "Expand all", exact: true }).click();
  for (const entry of catalogue.sections)
    for (const rule of entry.items)
      await expect(page.getByText(rule.text, { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Collapse all", exact: true }).click();
  await expect(
    page.getByText("Register separately for the examination."),
  ).not.toBeVisible();
});

test("degree changes clear old searches and show the new degree's credits", async ({
  page,
}) => {
  await openRules(page);
  await page
    .getByRole("textbox", { name: "Search all rules" })
    .fill("already counted");
  await page
    .getByRole("combobox", { name: "Degree program", exact: true })
    .click();
  await page.getByRole("option", { name: "B.Sc. Physik", exact: true }).click();
  await expect(
    page.getByRole("textbox", { name: "Search all rules" }),
  ).toHaveValue("");
  await expect(
    page.getByRole("region", { name: "Degree at a glance" }),
  ).toContainText("180 LP total");
  await expect(
    page
      .getByRole("region", { name: "Degree at a glance" })
      .getByRole("button"),
  ).toHaveCount(2);
  await expect(
    page.getByText("Credits already counted in a Bachelor cannot count again."),
  ).not.toBeVisible();
});

test("the rules remain usable on a narrow screen", async ({
  page,
}, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openRules(page);
  await expect(
    page.getByRole("textbox", { name: "Search all rules" }),
  ).toBeVisible();
  await page
    .getByRole("navigation", { name: "Rule topics" })
    .getByRole("button", { name: /Recognition & abroad/ })
    .click();
  await page
    .getByRole("button", { name: "Earlier credits", exact: true })
    .click();
  await expect(
    page.getByText("Credits already counted in a Bachelor cannot count again."),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: testInfo.outputPath("degree-rules-mobile.png"),
    fullPage: true,
  });
});
