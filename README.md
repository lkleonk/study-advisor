![Modulio home page](ressources/home_page.png)

Website: [unimodulio.com](https://unimodulio.com) (the old `cs-modulio.com` redirects there until it is deactivated)

# Modulio — FU Berlin Study Consultant

Full-stack prototype for a FU Berlin study consultant, named **Modulio** (a nod to *Leistungspunkte* — the LP credits it helps you track).

The app supports multiple degree programs through a backend degree registry — currently the M.Sc. Informatik (SPO 2014), the M.Sc. Data Science (FU-Mitteilungen 18/2021), the B.Sc. Informatik (FU-Mitteilungen 23/2023), the B.Sc. and M.Sc. Physik (both FU-Mitteilungen 12/2024), and the B.Sc. Bioinformatik (FU-Mitteilungen 34/2023). Users pick their degree in the welcome dialog and can switch later from the header; each session is bound to one degree. The app answers questions from local resources and offers a read-only Course Registry of locally listed SoSe 2026 and WiSe 2026/27 offerings. Deterministic study-plan validation is enabled for the M.Sc. Informatik only; for the other degrees, uploaded transcripts are used as chat context without rule validation. B.Sc. Informatik maths courses are free-elective candidates only. It includes a standalone Next.js frontend and a FastAPI backend. It reuses architecture patterns from the parent `llm_chatbot` project, but all code lives inside `fu_berlin_cs_consultant/`.

## Screenshots

Agent flow:

![Agent flow](ressources/screenshot_agent_flow.png)

Study plan check (visualizes the proposed study plan, then validates it against the deterministic 2014 Master Informatik rules and flags missing credits or unmet requirements):

![Study plan](ressources/screenshot_study_plan.png)

## Scope

- No Postgres in phase 1.
- Course-offering lookup uses the local canonical course catalogue and exact semester data.
- LLM provider can be AcademicCloud or FU/local Ollama.
- Answers are advisory. Official FU Berlin documents and the examination office remain authoritative for real study decisions.

For M.Sc. Informatik (SPO 2014), the degree has four separate parts: **70 LP
Informatik + 10 LP Anwendungsbereich + 10 LP Wahlbereich + 30 LP Masterarbeit**.
The Informatik part comprises the 20/10/10 LP subject minima, 20 additional LP in
one specialization, and 10 LP of free Informatik choice. Wahlbereich credits do
not satisfy those minima. The whole-plan limits remain 1–2 Softwareprojekte and
2–4 Wissenschaftliches Arbeiten modules, including Wahlbereich. Bachelor-level
modules are capped at 15 LP across all allocations; credits already used for a
Bachelor degree or Master admission cannot count again. Unknown prior use is
flagged for confirmation. The structured Degree Rules catalogue, chat context,
and Python checks share this model; see [study-plan data](docs/study-plan-data.md).

Course choice also depends on fitting the checklist's module slots: check a
course's dedicated named module before using a broad topic module, and preserve
flexible slots for courses you want in later semesters. The Degree Rules tab,
copied rules, and chat adviser share the canonical slot list and this planning
guidance. External courses can be proposed for recognition with a reasoned
mapping of learning outcomes and workload; the Prüfungsausschuss decides the
recognition, and each target module can be counted only once.

The M.Sc. Informatik guidance also covers restrictions on rebooking completed
modules, professional work as a possible substitute for one Softwareprojekt,
separate course/exam registration, exam attempts and grade improvement, and
advance study-abroad agreements. These rules appear in Degree Rules, copied
rules, and chat reference context. They remain advisory: the plan checker does
not track the administrative records or decisions needed to establish eligibility.

## Documentation

Paths and commands are relative to this project root, regardless of its
checkout directory name. For architecture, start with the domain model, then
read the agent flow and API contracts.

| Topic | Reference |
| --- | --- |
| Degree registry, course data, and validation ownership | [Domain model](docs/domain-model.md) |
| Graph routes, state, nodes, and tracing | [Agent flow](docs/agent-flow.md) |
| Endpoints, sessions, and quotas | [Backend API](docs/backend-api.md) |
| Tabs, contexts, browser storage, and API integration | [Frontend architecture](docs/frontend.md) |
| Study-plan schemas and persistence | [Study-plan data](docs/study-plan-data.md) |
| Transcript ingestion | [PDF pipeline](docs/pdf_node.md), current implementation section |
| Data Science validator (runtime validation disabled) | [M.Sc. Data Science](docs/data_science_master.md) |
| Providers, SSH tunnel, and prompts | [LLM providers](docs/llm-providers.md) |
| Azure hosting, Compose, Caddy, and public origins | [Deployment](docs/deployment.md) |
| Terraform bootstrap and backend image setup | [Infrastructure](infra/README.md) |
| Frontend startup and mocked browser test | [Frontend README](frontend/README.md) |
| Contributor constraints and verification | [AGENTS.md](AGENTS.md) |

The [implementation checklist](implementation.md) and
[frontend plan](docs/fu_consultant_frontend_plan.md) retain earlier phases and
open ideas. The PDF document also preserves its original attachment proposal
after the current implementation summary. Proposed endpoints and components in
those plans are not evidence that they exist; use the current subsystem
references and code for exact behavior.

## Project Structure

```text
fu_berlin_cs_consultant/
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py              # App entrypoint
│   │   ├── routes.py            # API routes
│   │   ├── models.py            # Pydantic models
│   │   ├── settings.py          # Config
│   │   ├── domain/              # Course offerings, study plan logic, shared rule models
│   │   │   └── degrees/         # Degree registry: per-degree prompts, rules, catalogues
│   │   └── services/            # LLM providers, vector store, agent graph
│   │       ├── nodes/           # Agent graph nodes (course lookup, rule checker, ...)
│   │       └── states/          # Agent graph state
│   ├── tests/                   # Pytest suite
│   └── Dockerfile
├── frontend/                    # Next.js frontend
│   ├── src/
│   │   ├── app/                 # Pages & consultant UI components
│   │   ├── context/             # React context (settings)
│   │   ├── services/            # API client
│   │   ├── theme/               # MUI theme & colors
│   │   └── types/               # Shared API types
│   ├── public/                  # Static assets
│   └── Dockerfile
├── ressources/                  # Source documents & screenshots
├── docs/                        # Project docs & diagrams
├── docker-compose.yml
└── .env.example
```

## Environment

Create `.env` from `.env.example` and fill in the provider you want. Docker
Compose uses it for variable interpolation and passes backend settings into the
backend container. Optional secrets in `.env.local` override the corresponding
backend values from `.env`.

```bash
cp .env.example .env
```

Pick one provider via `LLM_PROVIDER`. Each provider reads its own `<PROVIDER>_*` vars; the others are ignored.

Deployment settings:

| Variable | Purpose | Local default |
| --- | --- | --- |
| `COMPOSE_BIND_ADDRESS` | Host address on which Compose publishes ports | `127.0.0.1` |
| `APP_DOMAIN` | Canonical public hostname served by Caddy | `localhost` |
| `APP_WWW_DOMAIN` | `www` hostname that Caddy redirects to `APP_DOMAIN` | `www.localhost` |
| `FRONTEND_PORT` | Host port for the optional local static-frontend preview | `3000` |
| `CONSULTANT_HOST` | Backend bind address inside its container | `0.0.0.0` |
| `CONSULTANT_PORT` | Backend host and container port | `8000` |
| `NEXT_PUBLIC_API_BASE_URL` | Browser-facing backend URL embedded in the static export during `next build` | `http://localhost:8000` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated exact frontend origins allowed by FastAPI | `http://localhost:3000` |
| `FORWARDED_ALLOW_IPS` | Proxy IPs/CIDRs allowed to supply forwarded client IPs | `127.0.0.1` |

`CORS_ALLOWED_ORIGINS` entries must contain only scheme, hostname, and optional
port, with no path. Example: `https://consultant.example.com,https://admin.example.com`.

`NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_ENABLE_DEV_TOOLS` are public,
build-time values. Rebuild and redeploy `frontend/out` after changing either
one. Never place API keys or passwords in a `NEXT_PUBLIC_*` variable.

For production, explicitly set `NEXT_PUBLIC_API_BASE_URL`,
`CORS_ALLOWED_ORIGINS`, `LLM_PROVIDER`, and the selected provider's base URL,
model, and credentials. The bind addresses and ports have safe local defaults
but should still be reviewed before deployment.

AcademicCloud (hosted API):

```env
LLM_PROVIDER=academiccloud
ACADEMICCLOUD_MODEL=qwen3-30b-a3b-instruct-2507
# ACADEMICCLOUD_API_KEY goes in .env.local
```

FU Ollama (cuda01 via auto SSH tunnel — no extra flag needed):

```env
LLM_PROVIDER=fu_ollama
FU_OLLAMA_MODEL=llama3.2
FU_SSH_HOST=cuda01.imp.fu-berlin.de
FU_SSH_PORT=22
# FU_SSH_USER and FU_SSH_PASSWORD go in .env.local
```

Local Ollama (running on the host machine):

```env
LLM_PROVIDER=local_ollama
LOCAL_OLLAMA_HOST=http://host.docker.internal:11434
LOCAL_OLLAMA_MODEL=llama3.2
```

Optional agent-flow tuning:

```env
AGENT_COURSE_SELECTOR_HISTORY_TURNS=2
AGENT_COURSE_SELECTOR_MAX_KEYS=20
AGENT_COURSE_SELECTOR_INCLUDE_SEMESTERS_NOTE=true
AGENT_ANSWER_COMPOSER_HISTORY_TURNS=4
```

Daily usage limits:

```env
DAILY_GLOBAL_ACTIONS=150
DAILY_USER_ACTIONS=60
```

Both limits count the same unit: one user action, meaning one chat message or
transcript upload. `DAILY_GLOBAL_ACTIONS` is shared by every client;
`DAILY_USER_ACTIONS` applies per client IP. Neither counts individual LLM calls,
of which one action makes several. Creating or
deleting a session, reading program rules or course offerings, and checking
health do not consume user actions.

`GET /api/usage` exposes the current client-IP action allowance without
consuming it. Successful chat and transcript responses also carry
`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and
`X-RateLimit-Scope` headers. The frontend shows a clickable allowance chip and
warns once per reset period when ten or fewer actions remain.

These counters are deliberately process-local Python state. They reset at
00:00 UTC and whenever the backend restarts. Run a single backend worker if the
configured numbers must remain the effective limits; each additional process
would have its own counters.

In-memory session retention:

```env
SESSION_INACTIVITY_TTL_SECONDS=172800
SESSION_CLEANUP_INTERVAL_SECONDS=300
```

Sessions are deleted after 48 hours without a message or transcript upload.
Cleanup runs opportunistically during later session activity, so no scheduler is
required. The production-visible Settings `Reset conversation` button calls
`DELETE /api/sessions/{session_id}`
before clearing browser state. Session cleanup does not delete WizardFlow trace
files; trace retention remains a separate operational concern.

Frontend developer diagnostics are build-time gated:

```env
NEXT_PUBLIC_ENABLE_DEV_TOOLS=false
```

When disabled, API/session diagnostics, health details, and dummy data are
hidden. Request allowance, chat download, and `Reset conversation` remain
available. The chat download is produced locally as Markdown and never sent to
the backend.

Semester coverage is not configured manually. The course selector derives
available semesters from the session degree's projection of the canonical course
catalogue and `backend/app/domain/data/course_offerings/<semester>.json` files.
The backend validates their cross-file course IDs, degree module mappings, and
area assignments at startup.

## Local Development With Docker Compose

Create the local configuration, add the secret required by the selected LLM
provider, then build and start the backend plus an optional static-frontend
preview:

```bash
cp .env.example .env
# Add ACADEMICCLOUD_API_KEY or the selected provider's credentials to
# .env.local. Both files are ignored by Git.
cd frontend && npm run build:local && cd ..
docker compose --profile frontend-preview up --build
```

`npm run build:local` bakes `http://localhost:8000` as the API base URL and
enables the developer tools. Both `build:local` and `build:prod` work the same
on Linux, macOS, and Windows (`build:local` sets its variables via `cross-env`).
The generated `frontend/out/` directory is gitignored. Build production exports
with `npm run build:prod` and upload them separately (see the production
section below).

The preview Docker image builds its own export with developer tools off by
default; the host `build:local` output is a separate artifact. See
[frontend build details](frontend/README.md).

The default local endpoints are:

```text
Frontend: http://localhost:3000/consultant
Backend:  http://localhost:8000
API docs: http://localhost:8000/docs
```

Changing `NEXT_PUBLIC_API_BASE_URL` requires a static export rebuild. Use:

```bash
cd frontend && npm run build:local && cd ..
docker compose --profile frontend-preview up --build -d
```

To build the Docker static preview (its Node builder creates a separate export
with the Dockerfile's local defaults):

```bash
docker compose build backend
docker compose --profile frontend-preview build frontend
docker compose --profile frontend-preview up
```

Follow runtime logs after services start:

```bash
docker compose logs -f backend frontend
```

The backend Dockerfile has timeouts around apt:

- package index update: 300 seconds
- system dependency install: 600 seconds

The image switches Debian's default package sources from HTTP to HTTPS before
updating the package index. If one of the guarded apt commands still times out,
the problem is Debian mirror access from Docker rather than Python dependency
resolution.

## Production Deployment

Production uses Azure Storage for the static frontend and Azure Container Apps
for the backend. Start with [infra/README.md](infra/README.md) for provisioning
and [docs/deployment.md](docs/deployment.md) for frontend origins, CORS, and
Cloudflare configuration.

### Previous DigitalOcean Droplet Deployment

The production Compose profile adds Caddy. Caddy terminates HTTPS, serves the
locally built static frontend export, and proxies backend paths over the
internal Compose network. There is no Node.js frontend process on the Droplet.
The frontend is built locally and shipped as a static artifact specifically to
keep the build off the Droplet, which is resource-constrained; the server only
serves files and runs the backend. The backend port remains published only on
host loopback for diagnostics:

```text
Internet -> Caddy :80/:443 -> frontend/out static files
                           -> backend:8000 for /api, /health, and API docs
```

Prerequisites:

- A Droplet with Docker Engine and the Docker Compose plugin installed.
- A domain whose DNS record points to the Droplet.
- A firewall allowing SSH, HTTP, HTTPS, and optionally HTTPS/UDP for HTTP/3.
  Do not expose application ports publicly.

Build the static export on the local machine with the production public API
origin. `frontend/out/` is gitignored; upload its refreshed contents separately
when deploying the updated source revision.

```bash
cd frontend
npm run build:prod
cd ..
```

`build:prod` (like plain `npm run build`) reads production values from the
local, gitignored `frontend/.env.production`. Copy `frontend/.env.example` to
that path and fill in your deployment values first. Shell variables and local
environment files can override those values. After testing with `build:local`,
run `build:prod` again before uploading `frontend/out/`; do not commit either
the populated environment file or the generated export.

Create the production environment on the server and restrict its permissions:

```bash
cp .env.example .env
chmod 600 .env
```

Example production values for a single-domain deployment:

```env
COMPOSE_BIND_ADDRESS=127.0.0.1
FRONTEND_PORT=3000
CONSULTANT_HOST=0.0.0.0
CONSULTANT_PORT=8000

# Public DNS name only; do not include https:// or a path.
APP_DOMAIN=example.com
APP_WWW_DOMAIN=www.example.com
CADDY_HTTP_PORT=80
CADDY_HTTPS_PORT=443

NEXT_PUBLIC_API_BASE_URL=https://example.com
CORS_ALLOWED_ORIGINS=https://example.com
NEXT_PUBLIC_ENABLE_DEV_TOOLS=false

# The backend port is loopback-only, so only local processes can reach it.
# Trust forwarded client IPs from the host reverse proxy/Docker gateway.
FORWARDED_ALLOW_IPS=*

LLM_PROVIDER=academiccloud
ACADEMICCLOUD_BASE_URL=https://provider.example.com/v1
ACADEMICCLOUD_MODEL=your-model-name
ACADEMICCLOUD_API_KEY=replace-with-the-real-secret-on-the-server

WIZARDFLOW_ENABLED=false
```

The placeholder values above are examples only. Use the real provider URL,
model, and secret for the selected provider. Do not commit the production
`.env` file.

`FORWARDED_ALLOW_IPS=*` is appropriate here only while the backend is not
published publicly. Caddy supplies the original client address through
forwarded headers, which keeps per-client quotas working.

Create an `A` record (and `AAAA` only when IPv6 is configured) from
`APP_DOMAIN` to the Droplet. Create `APP_WWW_DOMAIN` as a DNS alias for the
same host; Caddy redirects it permanently to `APP_DOMAIN`. Ensure ports 80 and
443 are free, then deploy the production profile:

```bash
docker compose --profile production up --build -d
docker compose ps
docker compose logs -f caddy backend
```

Caddy obtains and renews the TLS certificate automatically. Certificate state
is persisted in the `caddy_data` volume; do not delete that volume during normal
deployments. Check certificate or routing failures with
`docker compose logs --tail=200 caddy`.

After any `NEXT_PUBLIC_*` change, rebuild the static export locally and upload
the refreshed `frontend/out/` directory before restarting Caddy. Backend-only
environment changes require a container recreation but not an image rebuild.

Production now runs on Azure (see `docs/deployment.md`); the Droplet setup
above is the previous single-server deployment.

Production frontend:

```text
https://unimodulio.com/
```

Production health check (the static site has no `/health`; use the Container
App URL from `terraform output -raw backend_url`):

```text
<backend_url>/health
```

## WizardFlow Traces

WizardFlow 0.9.0 uses `with trace.workflow() as run` to finalize each request,
including failures, and node context managers to capture execution timing.
Chat graph nodes and transcript parsing/validation share the same scoped API.
Per-request tracing opt-out uses no-op scopes and writes no trace data.

WizardFlow tracing is enabled by default. Each chat request and transcript
upload receives an SDK-generated workflow ID, and each active agent node writes payloads into a
JSONL trace under `backend/traces/`. Docker persists `/app/traces` to that host
directory.

LLM-backed nodes record:

```text
llm_input  -> {"prompt": "...", "msg": "..."}
llm_output -> raw model response
llm_error  -> exception type and message, when an LLM call or output processing fails
```

Deterministic nodes record `node_input` and `node_output`. Only executed application nodes
are recorded; synthetic `__start__` and `__end__` markers are omitted. Trace
failures are logged but do not fail consultant requests.

Configuration:

```env
WIZARDFLOW_ENABLED=true
WIZARDFLOW_OUTPUT_DIR=traces
WIZARDFLOW_FILE_PREFIX=fu_cs_consultant
```

For a university production deployment that promises session-only temporary
storage, set `WIZARDFLOW_ENABLED=false`. When tracing is enabled, the welcome
dialog discloses that unredacted diagnostic files may outlive in-memory session
state.

All traffic is written into one long-lived trace file per backend process. To
start a fresh timestamped trace file without restarting the backend (for
example before a manual test run), use the `New Trace File` button in the
Settings developer section, or call the endpoint directly:

```bash
curl -X POST http://localhost:8000/api/tracing/reinit
```

The old file is left as-is, open messages carry over into the new file, and a
disabled tracer answers HTTP 409 with `error_code == "tracing_disabled"`.

To generate a sample trace, run from `backend/` in PowerShell with local LLM
credentials configured:

```powershell
$env:WIZARDFLOW_ENABLED = 'true'
uv run --isolated --python 3.12.10 --with-requirements requirements.txt python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

In a second PowerShell terminal, create a session and ask a sample question:

```powershell
$session = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8011/api/sessions' -ContentType 'application/json' -Body '{"degree":"msc_informatik"}'
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8011/api/sessions/$($session.session_id)/message" -ContentType 'application/json' -Body '{"content":"How many total credit points do I need for M.Sc. Informatik? Please answer briefly.","tracing_enabled":true}'
```

Open the generated `backend/traces/*.jsonl` file in
[getwizardflow.com](https://getwizardflow.com). Provider rate limits can cause
requests to fail; failed workflows are also finalized in the trace.

Trace files contain unredacted system prompts, chat messages, and extracted
transcript text. Treat `backend/traces/` as sensitive local data; it is excluded
from Git.

## API

List the supported degree programs:

```bash
curl http://localhost:8000/api/degrees
```

Create a session (degree defaults to `msc_informatik` when the body is omitted):

```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d "{\"degree\":\"msc_data_science\"}"
```

Read the degree-rule catalogue for one degree:

```bash
curl "http://localhost:8000/api/program-rules?degree=msc_informatik"
```

Read locally listed course offerings for one degree:

```bash
curl "http://localhost:8000/api/course-offerings?degree=msc_informatik"
```

Delete a session and its in-memory LangGraph state:

```bash
curl -X DELETE http://localhost:8000/api/sessions/<session-id>
```

Read the current client request allowance and retention information:

```bash
curl http://localhost:8000/api/usage
```

Ask a question:

```bash
curl -X POST http://localhost:8000/api/sessions/<session-id>/message \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"Wie viele LP brauche ich im Anwendungsbereich?\"}"
```

Check a study plan:

```bash
curl -X POST http://localhost:8000/api/sessions/<session-id>/message \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"Bitte pruefe meinen Studienplan mit Vertiefung Praktische Informatik: Softwareprojekt Praktische Informatik B 10 LP, Wissenschaftliches Arbeiten Praktische Informatik A 5 LP, Projektmanagement 5 LP, Kuenstliche Intelligenz 5 LP, Datenbanktechnologie 5 LP, Rechnersicherheit 10 LP, Algorithmische Geometrie 10 LP, Modelchecking 10 LP, Betriebssysteme 10 LP, Wissenschaftliches Arbeiten Technische Informatik A 5 LP, Mobilkommunikation 5 LP, Anwendungsmodul A 10 LP.\"}"
```

Health:

```bash
curl http://localhost:8000/health
```

## Tests

From `backend/`:

```bash
uv run --isolated --python 3.12.10 --with-requirements requirements.txt --with pytest python -m pytest -q
```

The backend suite covers degree rules, catalogue projections, agent helpers,
PDF processing, API contracts, quotas, session lifecycle, settings, and tracing.
GitHub Actions runs the compile check and backend suite on pushes and pull
requests to `main` (`.github/workflows/backend-tests.yml`).

From `frontend/`:

```bash
npm run lint
npx tsc --noEmit
npm run build
```

The mocked browser journey is documented in [frontend/README.md](frontend/README.md).
It verifies the consultation flow without a live backend or LLM.
