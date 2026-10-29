# Deployment (Azure / Docker Compose / Caddy)

Production uses Azure Storage static website hosting and Azure Container Apps;
see [Azure infrastructure](../infra/README.md). The Compose production profile
below is the previous single-server deployment and remains available as an
alternative.

`docker-compose.yml` starts the backend locally. The optional static-frontend
preview uses the `frontend-preview` profile:

```text
frontend preview -> http://localhost:3000/
backend          -> http://localhost:8000
```

The optional `production` profile also starts Caddy on ports 80/443. Caddy
terminates HTTPS, serves `frontend/out` directly from `/srv`, and proxies only
backend traffic over the internal Compose network. Production therefore runs no
Node.js frontend container. Its certificate state persists in the `caddy_data`
volume.

## Two Caddyfiles, distinct roles

- Root `Caddyfile` belongs to the production `caddy` service: TLS, the `www`
  redirect, backend proxying, and the static export.
- `frontend/Caddyfile.preview` belongs only to the optional `frontend-preview`
  service; it is a minimal local static-file server and is **not** used in the
  production request path.

## Static frontend export

The frontend is a static Next.js export (`output: "export"`). Build it on the
local machine with `npm run build`; the generated `frontend/out/` directory is a
gitignored deployment artifact and must be rebuilt and uploaded separately
before deployment. The browser-facing API base URL is baked into that export. The optional Docker
preview image creates its own export in a Node builder stage and copies it into
Caddy. Its `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_ENABLE_DEV_TOOLS` build
arguments default to the following values (Compose does not override them):

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_DEV_TOOLS=false
```

`NEXT_PUBLIC_API_BASE_URL` is intentionally host-facing because the JavaScript
runs in the user's browser, not inside the Docker network.

## Environment

Compose uses `.env` as the backend env file. Keep `.env.example` aligned when
adding required runtime variables.

Compose publishes application ports on `COMPOSE_BIND_ADDRESS` and reads
`FRONTEND_PORT` (preview only), `CONSULTANT_PORT`, `CORS_ALLOWED_ORIGINS`, and
`FORWARDED_ALLOW_IPS` from `.env`. Keep the application bind address on loopback
when the production Caddy profile is enabled. Production additionally requires
`APP_DOMAIN`, a static export built with the matching `NEXT_PUBLIC_API_BASE_URL`,
and matching CORS configuration.

## Build notes

The backend Dockerfile intentionally wraps apt update/install in timeouts. If
apt times out, investigate Docker network access to Debian mirrors before
changing Python dependencies.

For the Compose production profile, first rebuild `frontend/out/` locally,
upload the gitignored export separately, and deploy the updated source revision.
Then run the production Compose profile; only `backend` and Caddy run. Use
`docker compose logs -f backend caddy` when production runtime behavior is unclear.

## Azure production architecture

The Azure/Terraform stack lives in `infra/`. It provisions Azure Storage
static website hosting for the frontend, ACR plus Azure Container Apps for the
backend, Key Vault with managed-identity access for the AcademicCloud API key,
and Log Analytics. The Container App is fixed at one warm replica while sessions and
quotas remain process-local, and WizardFlow is disabled because no persistent
trace storage is provisioned.

The static website has no reverse proxy, so `/api` on `unimodulio.com` does not
reach the backend. The local, gitignored `frontend/.env.production` therefore sets
`NEXT_PUBLIC_API_BASE_URL` to the Container App URL (`terraform output -raw
backend_url`); the backend's CORS allows `https://unimodulio.com`. Change it to
`https://api.unimodulio.com` once that custom domain is set up.

The Storage static website serves the custom domain `unimodulio.com`
(`frontend_custom_domain`). Azure Storage allows one custom domain per account
and rejects unregistered host names with `400 InvalidUri`. Ownership is proven
indirectly via the Cloudflare record `asverify` → `asverify.<storage
account>.blob.core.windows.net` (DNS only), so `@` can stay proxied. Cloudflare
SSL/TLS must be "Full" (Azure's certificate is for `*.web.core.windows.net`),
and `www.unimodulio.com` is a Cloudflare redirect to the apex. The new origin
must also be in the backend CORS origins.

The old domain `cs-modulio.com` is still active but only as a redirect: its
Cloudflare zone has a proxied placeholder `A` record (`192.0.2.1`) plus a proxied
`www` CNAME, and a Redirect Rule sends both host names with 301 to
`https://unimodulio.com` (path and query kept). The old Caddy server no longer
receives traffic. The domain will be fully deactivated soon; its CORS entries
can then be dropped from `terraform.tfvars`.

Infrastructure creation uses a two-phase bootstrap so neither an API key nor a
nonexistent ACR image is required during the first apply. See `infra/README.md`
for the exact sequence. The backend `api.` domain, remote Terraform state,
and GitHub Actions application releases are intentionally deferred.

Azure for Students policies may limit both deployment regions and ACR Tasks.
The stack supports a backend-only deployment with `deploy_frontend = false`;
when ACR Tasks are disabled, build the backend image with local Docker and push
it to ACR before enabling `deploy_backend`. The concrete commands and region
notes are in `infra/README.md`.
