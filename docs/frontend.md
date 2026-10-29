# Frontend Architecture

The static Next.js export is served at `/` (and `/consultant`) and uses React,
TypeScript, Material UI, and the App Router. Keep all frontend edits inside
the project's `frontend/` directory.

## Tabs

- `Chat`: session creation, message send, assistant response, citations, and
  plan-check result summary. Message content is rendered as GitHub-flavored
  Markdown (including emphasis, lists, and safe inline links); raw HTML is not
  rendered.
- `Study Plan`: student-specific extracted plan, modules, LP totals, Wahlbereich
  data, and validation issues. Shown only for degrees whose `GET /api/degrees`
  entry has `plan_validation_enabled` (currently M.Sc. Informatik); for other
  degrees the tab, its panel, and the degree-switch "Open Study Plan" shortcut
  are hidden, while PDF upload in the chat still works as chat-only context.
  Needs dedicated study-plan API endpoints before it can be complete.
- `Degree Rules`: read-only rendering of `GET /api/program-rules`, plus a
  persistent external link to the Modulio degree-structure escape room, and a
  "Copy" button (tooltip explains it) that renders the loaded catalogue
  client-side as plain-text degree rules for pasting into an external AI
  (`buildDegreeRulesText` in `degreeRulesText.ts`: two framing lines plus the
  rules; Modulio's backend prompts are never included). For M.Sc. Informatik,
  the catalogue orders the four degree components first (70/10/10/30 LP), then
  the shared restrictions; the overall-structure accordion opens by default.
  The same corrected catalogue supplies chat reference context and copied rules.
  Its checklist-planning section explains course-to-module placement, preserving
  flexible slots for future courses, and external recognition; the module-slot
  lists come from the backend catalogue rather than frontend-owned data.
  Additional M.Sc. Informatik sections cover rebooking completed modules,
  professional-work recognition, exam registration, attempts/grade improvement,
  and study abroad. They are advisory text with official sources and are included
  in copied rules; the Study Plan's arithmetic verdict does not verify these
  administrative conditions or perform any registration/recognition action.
- `Course Registry`: read-only, locally filterable rendering of the selected
  degree's `GET /api/course-offerings` projection. It lists only courses present
  in the local semester-offering data and does not consume the request allowance.
  Its source caveat is compact secondary text; data loads automatically, with a
  retry action shown only after an error. Each card lists the first appointment
  of each weekly lecture slot (max four) and, for lectures, the Übung groups: one
  group inline, several behind an „Übungen (n groups)“ toggle, nothing while the
  VV lists none. The Übung line carries its own VV link when `uebung_url` is set.
- `Settings`: dark mode, request allowance, production-visible reset
  conversation, plus optional developer diagnostics.

## Conventions

- Use MUI components and `sx` styling. Do not add Tailwind.
- Prefer theme tokens over hardcoded colors.
- Use icon buttons where an established icon exists.
- Keep the first screen as the actual consultant app, not a landing page.
- Keep `SettingsContext` / `UsageContext` / `DegreeContext` as the frontend
  sources of truth for dark mode, request allowance/retention, and degree choice
  respectively (see Client State below).
- Keep API calls in `frontend/src/services/api.ts` and shared TypeScript API
  contracts in `frontend/src/types/api.ts`.
- Do not put degree-rule validation logic in TypeScript. The frontend renders
  backend data and validation results.
- If i18n is added later, use `next-intl` and update all locale files together.

The browser-facing backend origin comes from `NEXT_PUBLIC_API_BASE_URL`. This
public value is embedded during `next build`, so rebuild and upload the
gitignored `frontend/out` deployment artifact after changing it. The local
Compose default is
`http://localhost:8000`. Azure production uses the separate public HTTPS
Container App origin because Storage static hosting cannot proxy `/api`. See
[deployment](deployment.md) for configuration.

For the previous single-server deployment, the optional Compose `production`
profile runs Caddy on ports 80/443. Caddy
serves the locally built `frontend/out` directory directly and proxies
backend/API-documentation paths on the same public origin; no Node.js frontend
container runs in production. `NEXT_PUBLIC_API_BASE_URL` and
`CORS_ALLOWED_ORIGINS` should both use `https://<APP_DOMAIN>`.

## Client State

- `SettingsContext` owns dark mode.
- MUI CSS color schemes and `InitColorSchemeScript` apply the persisted mode
  before the first browser paint. `fu-consultant-dark-mode` stores `light` or
  `dark`; a pre-paint migration maps the legacy boolean values for returning
  users.
- `UsageContext` owns the current client-IP action allowance and runtime
  retention information returned by `GET /api/usage`.
- `DegreeContext` owns the chosen degree program. It fetches the available
  degrees from `GET /api/degrees` (with a built-in fallback list for display
  when the backend is unreachable) and persists the choice in `localStorage`.
  Session creation sends the degree; the Degree Rules and Course Registry tabs
  fetch `GET /api/program-rules?degree=<id>` and
  `GET /api/course-offerings?degree=<id>` respectively.
- The session ID and rendered chat are kept in `sessionStorage`.
- Study Plan totals keep Informatik, Anwendungsbereich, and Wahlbereich separate.
  Modules show known Bachelor/admission credit reuse or unconfirmed Bachelor-level
  history. Older saved plans may omit the two prior-use fields and display them
  as unknown; the frontend does not infer recognition eligibility.
- The welcome-dialog version is kept in `localStorage` so material disclosure
  changes can display the dialog again. The dialog also reopens when no degree
  choice is stored.

## Degree Choice And Switching

The welcome dialog opens with card-style toggle buttons for the degree
programs; `Start consultation` stays disabled until one is selected. After the
welcome, the header subtitle is a compact degree switcher (`Select`). Changing
it with an active session or chat opens `DegreeSwitchDialog`, which warns that
the chat, uploaded study plan, and validation results will be discarded and
offers `Download chat` plus a shortcut to the Study Plan tab to print the
module summary first (that shortcut cancels the switch). Confirming deletes
the backend session, clears local chat/study-plan state, and the next message
creates a session for the new degree. With nothing to lose, the switch happens
immediately without the dialog.

## Request Allowance

The usage indicator (a `Usage: remaining/limit requests · resets <time>` chip
with a data-usage icon) and the chat download action live together in a
slim, non-scrolling strip at the top of the Chat tab, since chat and
transcript actions are what consume the allowance; clicking the chip opens
`RequestUsageDialog`. The download action is a labeled `Download` button
(not icon-only) whose tooltip states that the chat is not persisted and must
be downloaded to keep a copy, since session chat only lives in
`sessionStorage`. The global header holds only the logo/degree switcher and
the tab strip, which fills the remaining bar width edge to edge (each tab
sharing equal width); on smaller screens the tabs wrap to their own
full-width row below the logo. Chat and transcript responses update the
context from `X-RateLimit-*` headers with scope `user_action`; headers with any
other scope are dropped by `parseUsageHeaders`, so a service-wide limit is never
rendered as a user's own allowance. A warning dialog is shown once per reset
period when between one and ten requests remain.

The chip shows the caller's own allowance only. The shared service-wide budget
(`GET /api/usage` -> `service`) appears one level in, in `RequestUsageDialog`
under the personal figures: remaining count, a progress bar that turns amber past
80% use, and — when it is exhausted — a warning that requests will fail even
though the user still has their own allowance left. Both numbers count the same
unit (one chat message or transcript upload), so they are directly comparable.
The dialog refreshes usage on open, which is what keeps the service figure
current; `updateQuota` only ever merges the caller's own quota from response
headers and leaves `service` untouched. Failed chat/upload requests go through
`noteApiError`: it merges the caller's quota and, for a
`daily_service_quota_exceeded` 429 (which carries no per-user headers), refetches
usage so `service.remaining` shows the shared budget is gone. Quota 429s show no
separate error dialog.

When either allowance is exhausted (own `remaining <= 0`, or
`service.remaining <= 0`; the own limit wins when both are), `QuotaExhaustedDialog`
is shown once per scope and reset period, with wording for the user or
service-wide case. It offers "Copy degree rules" (fetches the selected degree's
program rules and copies `buildDegreeRulesText`, optionally with the chat so far
via an "Include our conversation so far" checkbox shown only when there are
messages) and "Go to Degree Rules". The Chat tab's input and transcript upload
are disabled while exhausted, the placeholder shows the reset time, and a line
under the input ("Continue in your own AI assistant") reopens the dialog. The
read-only Course Registry and Degree Rules tabs stay usable throughout.

## Chat Export And Reset

`Download chat` creates a Markdown file entirely in the browser. It includes
rendered messages, citations, and rule-check summaries, but not uploaded PDFs or
their extracted raw text.

`Reset conversation` remains visible in production. Its confirmation dialog
offers a download first, then calls `DELETE /api/sessions/{session_id}` and
clears local chat and study-plan state.

## Welcome And Data Disclosure

The versioned welcome dialog collects the degree-program choice and states that
the service is unofficial, answers may be wrong, requests are limited, session
data expires, and transcript text is processed by the configured LLM. When the
backend reports WizardFlow tracing as enabled, the dialog explicitly warns that
unredacted diagnostic traces may be retained separately from in-memory session
state.

## Developer Tools

`NEXT_PUBLIC_ENABLE_DEV_TOOLS=false` hides the API base URL, raw session ID,
health diagnostics, dummy data, manual health refresh, and the trace-file
button. It is a build-time UI switch, not a security boundary. Dark mode,
request allowance, chat download, and reset conversation remain available.

The developer section includes a persistent `Use bundled dummy data` switch for
the Course Registry. When enabled, the tab uses the explicitly fictional
fixtures under `app/consultant/dummy_data/` instead of requesting the backend,
and displays a visible dummy-preview warning. It is intended for static frontend
preview only and must never be presented as FU Berlin catalogue data.

The developer-only Study Plan preview switch displays a six-module partial
extract from `ressources/Leistungsuebersicht_Max_Mustermann_Demo.pdf` for
M.Sc. Informatik. The fixture lives under `app/consultant/dummy_data/`, hides
the transcript-upload action, and deliberately suppresses rule-check output so
the partial demo is never mistaken for a complete transcript or validation.

When the backend reports WizardFlow tracing as enabled
(`GET /api/usage` -> `diagnostic_tracing_enabled`), the developer section also
shows a `New Trace File` button. It calls `POST /api/tracing/reinit`, which
rotates the backend's WizardFlow trace to a fresh timestamped file (keeping the
graph and output configuration) and reports the new trace path. A disabled
tracer returns HTTP 409 with `error_code == "tracing_disabled"`.

## Diagnostic tracing opt-out

`SettingsContext` holds `tracingEnabled`, persisted to `localStorage` under
`TRACING_ENABLED_STORAGE_KEY` and defaulting to on — only a stored `"false"` opts
out. `ChatTab` and `TranscriptUpload` read it and pass it to `sendMessage` /
`uploadTranscript`, so a toggle applies to the next request without touching the
session.

It is a user-facing control, not a developer one, and is gated on
`usage?.diagnostic_tracing_enabled` rather than `DEV_TOOLS_ENABLED`: a Checkbox in
`WelcomeDialog` (consent framing, replacing the old warning caption) and a Switch
in the `SettingsTab` `Diagnostic tracing` section (matching the other settings
switches). When the deployment reports tracing off, neither renders at all —
absent rather than disabled, because a control that cannot change anything implies
the deployment might be tracing when it is not. A stored opt-out survives that and
still applies if the deployment turns tracing back on.

`CURRENT_WELCOME_VERSION` was bumped to `"3"` so returning users are shown the new
consent control once.
