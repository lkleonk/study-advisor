import { expect, test } from "@playwright/test";

test("a student can choose a degree and receive a chat reply", async ({ page }) => {
  // Record what the frontend sends so we can check it at the end.
  let selectedDegree: string | undefined;
  let sentMessage: string | undefined;

  // Prevent the optional WizardFlow popup from covering the chat during this test.
  await page.addInitScript(() => {
    localStorage.setItem("fu-consultant-wizardflow-promo-dismissed", "1");
  });

  // Replace backend requests with predictable responses; no real LLM is called.
  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;

    if (path === "/api/degrees" && request.method() === "GET") {
      // Offer one degree for the welcome dialog.
      await route.fulfill({ json: [{
        id: "msc_informatik",
        display_name: "M.Sc. Informatik",
        regulation: "2014 Studien- und Pruefungsordnung",
        plan_validation_enabled: true,
      }] });
      return;
    }

    if (path === "/api/usage" && request.method() === "GET") {
      // Give the student enough requests to use the chat.
      await route.fulfill({ json: {
        limit: 25,
        used: 0,
        remaining: 25,
        reset_at: "2099-01-01T00:00:00Z",
        service: { limit: 100, used: 0, remaining: 100 },
        session_inactivity_ttl_seconds: 7200,
        diagnostic_tracing_enabled: false,
        quota_scope: "client_ip",
      } });
      return;
    }

    if (path === "/api/sessions" && request.method() === "POST") {
      // Capture the chosen degree and pretend the backend created a session.
      selectedDegree = request.postDataJSON().degree;
      await route.fulfill({ json: { session_id: "test-session", degree: selectedDegree } });
      return;
    }

    if (path === "/api/sessions/test-session/message" && request.method() === "POST") {
      // Capture the question and return a fixed assistant reply.
      sentMessage = request.postDataJSON().content;
      await route.fulfill({ json: {
        reply: "The master's program requires 120 LP in total.",
        message_type: "degree_question",
        citations: [],
        rule_check_result: null,
        parsed_study_plan: null,
      } });
      return;
    }

    // Make any unhandled API request visible as a failure in the app.
    await route.fulfill({ status: 404, json: { detail: `Unexpected API request: ${path}` } });
  });

  // Open the app and choose the master's degree in the welcome dialog.
  await page.goto("/consultant");
  await expect(page.getByRole("dialog", { name: "Welcome to Modulio" })).toBeVisible();
  await page.getByRole("button", { name: /M\.Sc\. Informatik/ }).click();
  await page.getByRole("button", { name: "Start consultation" }).click();

  // Type a question and send it through the real chat UI.
  await page.getByPlaceholder("Message or upload a transcript PDF")
    .fill("How many LP do I need?");
  await page.getByRole("button", { name: "Send message" }).click();

  // Check both the displayed answer and the requests sent by the frontend.
  await expect(page.getByText("The master's program requires 120 LP in total.")).toBeVisible();
  expect(selectedDegree).toBe("msc_informatik");
  expect(sentMessage).toBe("How many LP do I need?");
});
