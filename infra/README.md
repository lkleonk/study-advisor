# Azure infrastructure

This directory provisions the first production Azure architecture:

```text
Azure Storage static website -> static frontend/out
Azure Container Apps  -> backend image from ACR
Azure Key Vault       -> AcademicCloud API key
Managed identity      -> ACRPull + Key Vault Secrets User
Log Analytics         -> Container Apps logs
```

Terraform owns infrastructure. GitHub Actions will later own application builds
and releases. The backend stays at exactly one warm replica because sessions and
quotas are process-local. WizardFlow is disabled because no persistent trace
storage is provisioned.

Set `deploy_frontend = false` when only the backend platform should be
provisioned. When enabled, Terraform creates an Azure Storage Account, enables
its static website feature, and exposes the exported frontend through the
storage account's `$web` container.

Azure for Students subscriptions can restrict resource locations. Use a
location allowed by the subscription policy (this deployment uses
`Switzerland North`).

## Prerequisites

- Terraform 1.8 or newer
- Azure CLI
- an Azure subscription
- permission to create resources and role assignments

Sign in and select the intended subscription:

```powershell
az login
az account set --subscription "<subscription-id>"
```

Copy the example variables and replace the subscription ID and globally unique
suffix. Do not commit the resulting `terraform.tfvars` file.

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out bootstrap.tfplan
terraform apply bootstrap.tfplan
```

The first apply deliberately leaves out the Container App. This lets Azure
create the empty registry and Key Vault without Terraform needing a nonexistent
backend image or placing the API key in Terraform state.

## Add the secret and first backend image

Run these commands from `infra/`. Enter the real API key only when prompted by
Azure CLI; do not put it in a command, shell history, or `.tfvars` file.

```powershell
$vaultName = terraform output -raw key_vault_name
$registryName = terraform output -raw container_registry_name
$apiKey = Read-Host "AcademicCloud API key" -AsSecureString
$credential = [System.Net.NetworkCredential]::new("", $apiKey)
az keyvault secret set --vault-name $vaultName --name academiccloud-api-key --value $credential.Password
$credential.Password = $null
az acr build --registry $registryName --image cs-modulio-backend:initial ../backend
```

Some Azure for Students subscriptions disable ACR Tasks, which makes
`az acr build` unavailable. In that case, build locally with Docker and push the
same tag to ACR:

```powershell
$registryServer = terraform output -raw container_registry_login_server
az acr login --name $registryName
docker build --tag "$registryServer/cs-modulio-backend:initial" ../backend
docker push "$registryServer/cs-modulio-backend:initial"
```

Set `deploy_backend = true` in `terraform.tfvars`, then create the Container App:

```powershell
terraform plan -out application.tfplan
terraform apply application.tfplan
terraform output
```

Check the generated endpoint:

```powershell
$backendUrl = terraform output -raw backend_url
Invoke-RestMethod "$backendUrl/health"
```

## What is intentionally deferred

- GitHub Actions workflows for frontend and backend releases
- `api.` custom domain for the backend (the frontend custom domain
  `unimodulio.com` is set via `frontend_custom_domain`; see
  `docs/deployment.md`)
- remote Terraform state
- shared session/quota persistence and horizontal scaling
- Azure Files for WizardFlow traces

These are separate steps so the first deployment remains understandable and
testable. A future frontend release workflow should authenticate to Azure and
upload `frontend/out/` to the Storage Account's `$web` container.
