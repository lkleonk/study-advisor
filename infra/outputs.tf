output "resource_group_name" {
  description = "Azure resource group containing the application."
  value       = azurerm_resource_group.main.name
}

output "container_registry_name" {
  description = "ACR name used by backend image builds."
  value       = azurerm_container_registry.main.name
}

output "container_registry_login_server" {
  description = "ACR login server used in backend image references."
  value       = azurerm_container_registry.main.login_server
}

output "key_vault_name" {
  description = "Key Vault name where the AcademicCloud API key must be added."
  value       = azurerm_key_vault.main.name
}

output "frontend_storage_account_name" {
  description = "Storage Account containing the exported frontend in its $web container."
  value       = var.deploy_frontend ? azurerm_storage_account.frontend[0].name : null
}

output "frontend_url" {
  description = "Azure Storage static website URL before Cloudflare is connected."
  value       = var.deploy_frontend ? trimsuffix(azurerm_storage_account.frontend[0].primary_web_endpoint, "/") : null
}

output "backend_url" {
  description = "Azure-generated backend URL, or null during bootstrap."
  value       = var.deploy_backend ? "https://${azurerm_container_app.backend[0].ingress[0].fqdn}" : null
}

output "backend_identity_client_id" {
  description = "Client ID of the backend managed identity."
  value       = azurerm_user_assigned_identity.backend.client_id
}
