data "azurerm_client_config" "current" {}

locals {
  base_name    = "${var.project_name}-${var.environment}-${var.name_suffix}"
  compact_name = replace(local.base_name, "-", "")

  resource_group_name        = "rg-${local.base_name}"
  container_registry_name    = substr("acr${local.compact_name}", 0, 50)
  container_environment_name = substr("cae-${local.base_name}", 0, 60)
  container_app_name         = substr("ca-${local.base_name}-api", 0, 32)
  identity_name              = substr("id-${local.base_name}-backend", 0, 128)
  key_vault_name             = trim(substr("kv-${local.base_name}", 0, 24), "-")
  log_workspace_name         = substr("log-${local.base_name}", 0, 63)
  frontend_storage_name      = substr("st${local.compact_name}", 0, 24)

  backend_image = "${azurerm_container_registry.main.login_server}/cs-modulio-backend:${var.backend_image_tag}"
  frontend_origins = distinct(concat(
    [var.frontend_origin],
    var.additional_frontend_origins,
    var.deploy_frontend ? [trimsuffix(azurerm_storage_account.frontend[0].primary_web_endpoint, "/")] : [],
  ))

  common_tags = merge(
    {
      application = var.project_name
      environment = var.environment
      managed-by  = "terraform"
    },
    var.tags,
  )
}

resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_container_registry" "main" {
  name                = local.container_registry_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = local.common_tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = local.log_workspace_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_container_app_environment" "main" {
  name                       = local.container_environment_name
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  logs_destination           = "log-analytics"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = local.common_tags
}

resource "azurerm_user_assigned_identity" "backend" {
  name                = local.identity_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  tags                = local.common_tags
}

resource "azurerm_key_vault" "main" {
  name                       = local.key_vault_name
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  soft_delete_retention_days = 7
  purge_protection_enabled   = true
  tags                       = local.common_tags
}

resource "azurerm_role_assignment" "backend_acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.backend.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "backend_key_vault_secrets" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.backend.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "deployer_key_vault_secrets" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_storage_account" "frontend" {
  count = var.deploy_frontend ? 1 : 0

  name                            = local.frontend_storage_name
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  account_kind                    = "StorageV2"
  access_tier                     = "Hot"
  https_traffic_only_enabled      = true
  min_tls_version                 = "TLS1_2"
  public_network_access_enabled   = true
  shared_access_key_enabled       = true
  allow_nested_items_to_be_public = false
  tags                            = local.common_tags

  dynamic "custom_domain" {
    for_each = var.frontend_custom_domain == null ? [] : [var.frontend_custom_domain]

    content {
      name          = custom_domain.value
      use_subdomain = true
    }
  }

  lifecycle {
    # Azure accepts use_subdomain but never reads it back, so it would show as a
    # pending change on every plan.
    ignore_changes = [
      custom_domain[0].use_subdomain,
    ]
  }
}

resource "azurerm_storage_account_static_website" "frontend" {
  count = var.deploy_frontend ? 1 : 0

  storage_account_id = azurerm_storage_account.frontend[0].id
  index_document     = "index.html"
  error_404_document = "404.html"
}

resource "azurerm_role_assignment" "deployer_frontend_storage" {
  count = var.deploy_frontend ? 1 : 0

  scope                = azurerm_storage_account.frontend[0].id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_container_app" "backend" {
  count = var.deploy_backend ? 1 : 0

  name                         = local.container_app_name
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"
  tags                         = local.common_tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.backend.id]
  }

  registry {
    server   = azurerm_container_registry.main.login_server
    identity = azurerm_user_assigned_identity.backend.id
  }

  secret {
    name                = "academiccloud-api-key"
    identity            = azurerm_user_assigned_identity.backend.id
    key_vault_secret_id = "${azurerm_key_vault.main.vault_uri}secrets/${var.academiccloud_secret_name}"
  }

  ingress {
    external_enabled           = true
    allow_insecure_connections = false
    target_port                = 8000
    transport                  = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "backend"
      image  = local.backend_image
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "CONSULTANT_HOST"
        value = "0.0.0.0"
      }

      env {
        name  = "CONSULTANT_PORT"
        value = "8000"
      }

      env {
        name  = "CORS_ALLOWED_ORIGINS"
        value = join(",", local.frontend_origins)
      }

      env {
        name  = "FORWARDED_ALLOW_IPS"
        value = "*"
      }

      env {
        name  = "LLM_PROVIDER"
        value = "academiccloud"
      }

      env {
        name  = "ACADEMICCLOUD_BASE_URL"
        value = var.academiccloud_base_url
      }

      env {
        name  = "ACADEMICCLOUD_MODEL"
        value = var.academiccloud_model
      }

      env {
        name        = "ACADEMICCLOUD_API_KEY"
        secret_name = "academiccloud-api-key"
      }

      env {
        name  = "DAILY_GLOBAL_ACTIONS"
        value = tostring(var.daily_global_actions)
      }

      env {
        name  = "DAILY_USER_ACTIONS"
        value = tostring(var.daily_user_actions)
      }

      env {
        name  = "WIZARDFLOW_ENABLED"
        value = "false"
      }

      liveness_probe {
        transport        = "HTTP"
        port             = 8000
        path             = "/health"
        initial_delay    = 10
        interval_seconds = 30
        timeout          = 5
      }

      readiness_probe {
        transport        = "HTTP"
        port             = 8000
        path             = "/health"
        initial_delay    = 5
        interval_seconds = 10
        timeout          = 5
      }
    }
  }

  depends_on = [
    azurerm_role_assignment.backend_acr_pull,
    azurerm_role_assignment.backend_key_vault_secrets,
  ]

  lifecycle {
    ignore_changes = [
      secret,
      template[0].container[0].image,
    ]
  }
}
