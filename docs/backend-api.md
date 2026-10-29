# Backend API

Routes are defined in `backend/app/routes.py`; treat that file as the source of
truth for the exact surface. This doc records the behavioural contract and the
constraints that are not obvious from the handler signatures.

Current public API:

```text
GET  /health
GET  /api/degrees
GET  /api/program-rules?degree=<degree_id>
GET  /api/course-offerings?degree=<degree_id>
GET  /api/usage
POST /api/tracing/reinit                # dev: rotate the WizardFlow trace file
POST /api/sessions                      # optional body {"degree": "<degree_id>"}
DELETE /api/sessions/{session_id}
POST /api/sessions/{session_id}/message      # body {"content": "...", "tracing_enabled": true}
POST /api/sessions/{session_id}/transcript   # multipart: file, tracing_enabled
```

## Sessions and degree binding

`POST /api/sessions` accepts an optional JSON body with a `degree` id (default
`msc_informatik`); unknown ids return HTTP 422 with
`detail.error_code == "unknown_degree"`. The degree id is seeded into the
LangGraph checkpoint at creation and returned in the response. All graph nodes
and transcript uploads read the session's degree from that state — the LLM never
chooses or infers it.

`POST /api/sessions/{session_id}/message` returns HTTP 502 with
`detail.error_code == "answer_generation_failed"` if answer generation fails or
produces an invalid or empty answer. The backend does not return a fallback reply
as a successful response.

`POST /api/sessions/{session_id}/transcript` accepts a multipart PDF upload
(field name `file`). See `docs/pdf_node.md`. For degrees without
`plan_validation_enabled` the transcript is only parsed into the session's
chat context: `rule_check_result` is `null` and the reply says that automatic
validation is unavailable.

For M.Sc. Informatik, chat and transcript responses include the parsed plan's
nullable module fields `counted_in_bachelor` and `used_for_master_admission`.
Missing fields in older plans default to unknown, independently of
`is_bachelor_module` (module level). Confirmed prior use produces validation
errors; unknown Bachelor-level credit history produces a warning. Rule-check
totals now separate 70 LP Informatik, 10 LP Anwendungsbereich, and 10 LP Wahlbereich;
subject minima exclude Wahlbereich. `graded_lp` and `ungraded_lp` exclude the
thesis. Existing `core_*_count` and `total_*_count` keys are retained: core counts
refer to the Informatik allocation and total counts include Wahlbereich.

## Read-only endpoints (no quota, no LLM)

These must never consume quota or invoke the LLM:

- `GET /api/degrees` lists registered degrees (id, display name, regulation,
  `plan_validation_enabled`) for
  the frontend picker. `bsc_informatik` exposes its 2023 degree rules and
  locally supplied SoSe 2026 and WiSe 2026/27 course offerings. It has no deterministic plan
  validation yet; availability in other semesters is unknown, and its 0084d
  maths listings are free-elective candidates rather than automatically
  recognised credit.
- `GET /api/program-rules` returns the structured display catalogue for the
  frontend Degree Rules tab, selected by the `degree` query parameter
  (default `msc_informatik`). It must not require LangGraph or an LLM.
  For M.Sc. Informatik it includes `checklist-planning`: practical placement
  advice and canonical module-slot names/LP generated from the course and degree
  catalogues. These slots describe credit targets, not semester availability.
- `GET /api/course-offerings` returns the selected degree's projected local
  course offerings for the Course Registry tab. It joins the canonical course,
  degree-mapping, and semester-offering layers in the domain model; the route
  never exposes raw source files or requires LangGraph, a session, an LLM, or
  quota consumption.
- `GET /api/usage` returns the current client-IP user-action allowance, UTC reset
  time, the shared service-wide allowance under `service`, the configured session
  inactivity TTL, and whether diagnostic WizardFlow tracing is enabled. The
  top-level `limit`/`used`/`remaining` are always the caller's own; `service` is
  the budget shared by everyone.

`POST /api/tracing/reinit` rotates the process-wide WizardFlow tracer to a fresh
timestamped trace file via `tracer.reinit()` (graph and output configuration are
kept; open messages carry over). It returns the new trace path, or HTTP 409 with
`detail.error_code == "tracing_disabled"` when tracing is off. It is triggered
manually from the frontend Settings developer section and must not consume quota
or invoke the LLM. The WizardFlow client is stored as the module global `tracer`
in `services/wizardflow_service.py`.

## Per-request tracing opt-out

`WIZARDFLOW_ENABLED` stays the deployment-level master switch. Under it, clients
may opt out of tracing per request: `tracing_enabled` on the message body and as
a multipart form field on the transcript upload, both defaulting to `true` so a
client that omits it is traced normally.

`SessionService` opens `wizardflow_service.workflow(enabled=..., title=...)`
for each request. Enabled requests use the SDK-generated `run.message_id`;
opted-out requests or a disabled process-wide tracer yield an empty ID.
`node_scope()` selects a disabled SDK client for empty IDs, so the same node
code runs without recording payloads or changing the shared tracer. Workflow
context exit finalizes enabled requests, including failures.

## Session lifecycle

`MemorySaver` is used for phase 1, so session state is in memory and lost on
backend restart. Sessions also expire after 48 hours of inactivity through
opportunistic cleanup. `DELETE /api/sessions/{session_id}` removes inactive
state immediately or defers deletion until an active request finishes.

Env knobs:

```text
SESSION_INACTIVITY_TTL_SECONDS
SESSION_CLEANUP_INTERVAL_SECONDS
```

## Usage quotas

Deployment quotas are process-local Python state in
`backend/app/services/quota_service.py`. They reset at 00:00 UTC and whenever the
backend process restarts. **Run one backend worker if the configured values must
remain the effective global limits** — multiple workers each get their own
counters.

Default limits:

```text
DAILY_GLOBAL_ACTIONS=150
DAILY_USER_ACTIONS=60
```

Both limits count the same unit: one user action, meaning one chat message or
transcript upload. `DAILY_GLOBAL_ACTIONS` is shared by every client;
`DAILY_USER_ACTIONS` applies per client IP. Neither counts individual LLM calls
— `ModelService` does no metering at all, deliberately, because one action fans
out across several nodes and charging per call made the two limits incomparable.
Sizing follows from that: the service-wide budget divided by the per-IP one is
roughly how many users can spend a full allowance in a day.

`DAILY_LLM_INVOCATIONS` is honoured as a fallback for the old name, but it used
to count LLM calls, so a value carried over from then buys roughly three times
the work it used to.

Both checks run under one lock in `consume_user_action()`, the caller's own limit
first — when they are at it, that is the truthful reason they are blocked,
whatever the service-wide state. Neither counter moves until both checks pass, so
a rejected action is never charged to the caller.

Creating or deleting sessions, reading program rules, and checking health do not
consume user actions. Quota exhaustion returns HTTP 429 with a structured error
payload and rate-limit headers: `daily_user_action_quota_exceeded` carries
`X-RateLimit-Scope: user_action`, and `daily_service_quota_exceeded` carries
`X-RateLimit-Scope: service_global`. Only the former describes a user's own
allowance and may be rendered as one; the frontend's `parseUsageHeaders` drops
anything else. There is no LLM concurrency cap.

Agent-flow tuning lives in `backend/app/services/agent_config.py`:

```text
AGENT_COURSE_SELECTOR_HISTORY_TURNS
AGENT_COURSE_SELECTOR_MAX_KEYS
AGENT_COURSE_SELECTOR_INCLUDE_SEMESTERS_NOTE
AGENT_COURSE_LOOKUP_INCLUDE_COURSE_URLS
AGENT_ANSWER_COMPOSER_HISTORY_TURNS
```

Do not duplicate available semesters in settings. The course selector derives
semester coverage from the session degree's projection of the canonical course
catalogue and semester offering files.
`AGENT_COURSE_LOOKUP_INCLUDE_COURSE_URLS` defaults to `false`; it controls URL
exposure in lookup-generated answer context and URL citations, not storage or
the read-only Course Registry response.
