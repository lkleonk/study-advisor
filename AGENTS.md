# AGENTS.md

Instructions for agents working in this project root (historically named
`fu_berlin_cs_consultant/`).
All project paths below are relative to the directory containing this file.

This file is the lean core: hard rules, orientation, and how to verify. Deep
per-subsystem reference lives in `docs/` — see the **Reference** index at the
bottom and read the relevant doc on demand rather than assuming.

## Hard Rules

- Do not use Git, except for read-only operations like `git diff`, `git status`, `git log`, and `git show`.
- Do not edit files outside this project root.
- Keep original files under `ressources/` untouched unless the user explicitly asks to update source material.
- Frontend work is allowed only inside this project root's `frontend/`.
- Course-offering sessions are first appointments `{date, start?, end?, room?}`,
  never the full timetable: `first_sessions` holds one per weekly lecture/seminar
  slot (max 4), `uebungen` (lectures only) one per Übung group, plus its VV
  `uebung_url`. There is no free-text description: module codes go in
  `fu_module_code` (module entry), crediting caveats in `credit_note` (placement);
  event numbers and lecturers are not stored. See
  `docs/domain-model.md`. Brief data subagents with this contract.

## Project Purpose

Public website: `https://unimodulio.com`. The old domain `cs-modulio.com`
(and `www.`) only 301-redirects there via a Cloudflare rule and will be fully
deactivated soon; do not reference it in new code or docs.

A FU Berlin study consultant for multiple degree programs, with a backend-first
architecture and a standalone Next.js frontend. Supported degrees live in a
registry (`backend/app/domain/degrees/`): currently `bsc_informatik`,
`bsc_physik`, `bsc_bioinformatik`, `msc_informatik`, `msc_data_science`, and `msc_physik`. It answers questions using exact local
course-offering lookup plus rules in prompts. Study-plan validation with
deterministic Python rules is switched on per degree via
`DegreeDefinition.plan_validation_enabled`; currently only `msc_informatik` has it
on, the other degrees answer from rules in prompts only. The core principle is **LLM parses → Python validates →
LLM explains**: the LLM may parse and explain, but must not be trusted for final
LP validation. Every session is bound to exactly one degree; the LLM never
chooses or infers the degree. The Course Registry is a second, read-only
consumer of the degree-scoped course-offering projection; it never reads source
JSON in the frontend or calls the LLM. See `docs/domain-model.md` for the degree
registry and data layers. To add a degree, follow the checklist under
"Adding a degree" in `docs/domain-model.md` (`bsc_physik` is the smallest template).

## Important Paths

```text
fu_berlin_cs_consultant/
  README.md
  implementation.md
  docker-compose.yml
  .env.example
  ressources/
  docs/
  infra/                         # Terraform: Azure backend + static frontend hosting
    main.tf
    variables.tf
    outputs.tf
    providers.tf
    terraform.tfvars.example
  backend/
    app/
      main.py
      routes.py
      models.py
      settings.py
      domain/
        catalog_data.py         # loads courses.json and degree_modules/*.json
        course_offerings.py
        program_rules.py        # generic catalogue models + prompt renderer
        rule_check.py           # shared RuleIssue/RuleCheckResult
        study_plan.py
        module_catalog.py
        data/courses.json              # shared canonical courses
        data/degree_modules/           # degree-specific credit mappings
        data/course_offerings/         # one JSON file per semester
        degrees/
          __init__.py           # registry: list_degrees(), get_degree(), DEFAULT_DEGREE_ID
          definition.py         # DegreeDefinition + DegreePrompts contract
          prompt_builder.py     # shared prompt templates; build_prompts(spec)
          bsc_informatik/       # each: __init__.py, prompts.py, degree_rules.py, program_rules.py
          bsc_physik/
          bsc_bioinformatik/    # joint FU/Charité programme
          msc_informatik/       # only degree with plan validation enabled
          msc_physik/
          msc_data_science/     # + module_catalog.py (canonical checklist modules)
      services/
      pdf/
    tests/
  frontend/
    Dockerfile                    # local Caddy-based static preview
    out/                          # exported site uploaded to Azure Storage $web
    src/
      app/
      components/
      context/                  # SettingsContext, UsageContext, DegreeContext
      services/
      theme/
      types/
```

There is no `backend/app/prompts.py`. Shared prompt templates live in
`domain/degrees/prompt_builder.py`; each `domain/degrees/<degree>/prompts.py`
declares only a `DegreePromptSpec`, rendered into `DegreeDefinition.prompts`;
nodes resolve them via `degree_for(state)` in `services/nodes/utils.py`.

The answer composer always receives the full degree rules; the optional
course-offering branch adds the looked-up offerings on top. Module names can
appear in both (e.g. B.Sc. module lists): this overlap is intended, not a bug.
Rules state requirements, offerings state semester availability.

## WizardFlow Tracing

WizardFlow is pinned in `backend/requirements.txt` (currently 0.9.0). Use
`wizardflow_service.workflow(enabled=..., title=...)` at the request boundary
and `node_scope(message_id, node_id, kind=...)` around node execution. Pass the
SDK-generated `run.message_id` through graph state; context managers own timing
and finalization, including failures. Do not restore manual `end_message` calls.
Keep shared transcript parsing/validation helpers scoped so both entry points
are traced. Per-request opt-out must use no-op scopes without changing the
process-wide tracer or writing payloads.

Preserve exact `llm_input` prompt/message payloads and existing event labels.
Trace files contain unredacted user data: keep `backend/traces/` gitignored and
use synthetic inputs for shareable samples. See `docs/agent-flow.md` for the
tracing contract and `README.md` for running and opening a sample JSONL trace.
Run `backend/tests/services/test_wizardflow_tracing.py` after tracing changes.

## Local CLI Notes

Use the shell provided by the current environment (for example zsh on macOS or
PowerShell on Windows). Use `rg` / `rg --files` for fast search when available,
and quote paths containing spaces. Do not assume the checkout directory name.
Run Docker Compose commands from the project root, backend Python/test commands
from `backend/`, and frontend commands from `frontend/`.

## Verification

Compile check:

```bash
python -m compileall -q backend/app
```

Focused tests from `backend/`:

```bash
uv run --isolated --python 3.12.10 --with-requirements requirements.txt --with pytest python -m pytest -q
```

Frontend checks from `frontend/`:

```bash
npm run lint
npx tsc --noEmit
npm run build
```

Runtime checks, when Docker and credentials are available:

```bash
docker compose build backend
cd frontend && npm run build && cd ..
docker compose --profile frontend-preview build frontend
docker compose --profile frontend-preview up
curl http://localhost:3000/
curl http://localhost:8000/health
```

Deployment/build gotchas (static export, Caddy, apt timeouts) are in
`docs/deployment.md`. Production uses Azure Container Apps for the backend, ACR
for its image, Key Vault for the LLM key, and Azure Storage Static Website for
`frontend/out/`; Terraform lives in `infra/`. Cloudflare owns public DNS/TLS.

Before applying infrastructure changes, run `terraform fmt -check` and
`terraform validate` from `infra/`, then inspect `terraform plan`. Never commit
`terraform.tfvars`, state, plans, credentials, or access tokens.

## Documentation Expectations

When behavior changes, update the relevant docs:

- Agent routing or node responsibilities: `docs/agent-flow.md` and `docs/agent-flow.html`
- Study plan state/schema/persistence: `docs/study-plan-data.md`
- Domain model (degrees, course data, program rules): `docs/domain-model.md`
- PDF transcript pipeline: `docs/pdf_node.md`
- Backend API surface/contracts: `docs/backend-api.md`
- Frontend architecture/conventions: `docs/frontend.md`
- LLM providers/model choice: `docs/llm-providers.md`
- Deployment/Docker/Caddy: `docs/deployment.md`
- Setup/API commands: `README.md`
- Implementation checklist: `implementation.md`

## Reference

See the [main README documentation section](README.md#documentation) for
subsystem links and the distinction between current references and historical plans.

Read the relevant doc before working on a subsystem; the code is always the
final source of truth for exact routes, schemas, and rule lists.

| Topic | Doc |
|---|---|
| Agent graph flow, nodes, routing, tracing | `docs/agent-flow.md` (+ `.html`) |
| Backend API routes, sessions, quotas, lifecycle | `docs/backend-api.md` |
| Degree registry, course-offering data, program rules, validation ownership | `docs/domain-model.md` |
| Study plan schemas, storage, data flow | `docs/study-plan-data.md` |
| M.Sc. Data Science degree structure | `docs/data_science_master.md` |
| PDF transcript upload pipeline | `docs/pdf_node.md` |
| Frontend architecture, state, tabs, conventions | `docs/frontend.md` |
| LLM providers, model choice, prompt conventions | `docs/llm-providers.md` |
| Local and Azure deployment / Terraform / Caddy / static export | `docs/deployment.md` + `infra/README.md` |
