# Modulio frontend

Next.js App Router, React, TypeScript, and Material UI frontend for the FU Berlin
study consultant. Both `/` and `/consultant/` show the consultant. Degree rules
and course offerings come from the FastAPI backend; the frontend does not run
degree validation or call the LLM directly.

## Local development

Run from `frontend/`:

```bash
npm ci
npm run dev
```

Open [the consultant](http://localhost:3000/consultant/). Start the backend
separately using the [project setup](../README.md). The default API origin is
`http://localhost:8000`; for another origin, set `NEXT_PUBLIC_API_BASE_URL` in
`frontend/.env.local` and restart the dev server. Backend CORS must allow the
frontend origin.

## Build and verification

```bash
npm run lint
npx tsc --noEmit
npm run build:local
```

`build:local` exports `out/` with the local API origin and developer tools on.
`build:prod` (or `build`) uses the production environment, including the local,
gitignored `.env.production` (copy `.env.example` and configure it first);
shell variables and local environment files can
override those values. Check overrides before producing a deployment artifact.
All `NEXT_PUBLIC_*` values are public and embedded at build time.

The configuration uses `output: "export"` and `trailingSlash: true`. Serve
`out/` with a static host or the Compose `frontend-preview` profile; `next start`
is not the serving path for this static export. The preview Dockerfile builds
the export in a Node builder stage, then copies it into the Caddy static-server
stage. Its build arguments default to the local API origin with developer tools
off; Compose currently supplies no overrides. Azure uploads and the root Caddy
service use the host-built `out/` instead. Rebuild that gitignored export with
`npm run build:prod` and upload it separately before a release.

Production uses Azure Storage static website hosting and a separate Azure
Container App API origin. See [deployment](../docs/deployment.md) and
[infrastructure](../infra/README.md).

## Legal pages

`/impressum` and `/datenschutz` use the same Material UI theme as the consultant.
Copy `.env.example` to `.env.production` (gitignored) and configure the public provider details at build time:

```env
NEXT_PUBLIC_LEGAL_NAME=Your provider name
NEXT_PUBLIC_LEGAL_STREET=Street and house number
NEXT_PUBLIC_LEGAL_CITY=Postal code and city
NEXT_PUBLIC_LEGAL_COUNTRY=Deutschland
NEXT_PUBLIC_LEGAL_EMAIL=contact@example.com
```

Keep the populated environment file local, or supply these values through deployment settings. They are rendered publicly on the deployed website, so this keeps them out of Git, not out of the Impressum. A visible warning is
shown on the legal pages while any value is missing. The privacy text also
contains deployment-specific sections that must be completed with the actual
hosting provider, LLM provider, recipients, and retention periods before a
public deployment.

## Browser test

Install dependencies and Playwright's Chromium browser, then run the frontend
journey test from this directory:

```bash
npm ci
npx playwright install chromium
npm run test:e2e
```

The test starts a local Next.js server and mocks the API responses in the
browser. It checks degree selection, session creation, message submission, and
reply rendering without making an LLM call. It does not test the live backend
or the correctness of an LLM answer.

The Playwright server uses port `32177` and a separate `.next-playwright`
build directory. Its configuration starts and stops that server automatically.

## Source map

- `src/app/consultant/components/`: consultant shell, tabs, dialogs, and uploads.
- `src/context/`: settings, degree selection, and usage allowance.
- `src/services/api.ts` and `src/types/api.ts`: HTTP client and response types.
- `src/theme/`: Material UI theme and persisted color scheme.
- `src/config/`: public build configuration and legal contact details.

See [frontend architecture](../docs/frontend.md) for storage, switching degrees,
quotas, diagnostic tracing, and developer previews.

## Private deployment configuration and generated output

The populated `.env.production` and generated `out/` directory are not tracked.
Run `npm run build` locally with your deployment environment, then upload the
resulting `out/` directory separately. A fresh checkout does not contain an export.
Do not force-add either path: the export embeds the configured legal contact data.

Docker build contexts exclude environment files. For a production site with the
configured legal details, use the local export workflow above. The Docker preview
uses placeholder legal details unless configuration is supplied separately.

Earlier commits still contain their original configuration and exports. When
sharing a sanitized source snapshot, reference the cleanup commit or a later
revision, and ask indexers to exclude earlier revisions and parent diffs.
