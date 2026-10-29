variable "subscription_id" {
  description = "Azure subscription that owns the deployment."
  type        = string
}

variable "name_suffix" {
  description = "Globally unique lowercase suffix used by ACR and Key Vault names (for example, your initials plus digits)."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{3,10}$", var.name_suffix))
    error_message = "name_suffix must contain 3-10 lowercase letters or digits."
  }
}

variable "project_name" {
  description = "Short project name used as the resource-name prefix."
  type        = string
  default     = "cs-modulio"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "project_name may contain only lowercase letters, digits, and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "prod"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.environment))
    error_message = "environment may contain only lowercase letters, digits, and hyphens."
  }
}

variable "location" {
  description = "Azure region for the resources."
  type        = string
  default     = "West Europe"
}

variable "deploy_backend" {
  description = "Create the Container App after its image and Key Vault secret exist. Keep false for the bootstrap apply."
  type        = bool
  default     = false
}

variable "deploy_frontend" {
  description = "Create the Azure Storage static website used for the exported frontend."
  type        = bool
  default     = true
}

variable "backend_image_tag" {
  description = "Existing backend image tag in ACR used for the first Container App revision. CI/CD owns later image updates."
  type        = string
  default     = "initial"

  validation {
    condition     = length(trimspace(var.backend_image_tag)) > 0
    error_message = "backend_image_tag must not be empty."
  }
}

variable "frontend_origin" {
  description = "Public frontend origin allowed by backend CORS, without a trailing slash."
  type        = string
  default     = "https://unimodulio.com"

  validation {
    condition     = startswith(var.frontend_origin, "https://") && !endswith(var.frontend_origin, "/")
    error_message = "frontend_origin must be an HTTPS origin without a trailing slash."
  }
}

variable "additional_frontend_origins" {
  description = "Additional HTTPS frontend origins allowed by backend CORS, without trailing slashes."
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for origin in var.additional_frontend_origins :
      startswith(origin, "https://") && !endswith(origin, "/")
    ])
    error_message = "additional_frontend_origins must contain HTTPS origins without trailing slashes."
  }
}

variable "frontend_custom_domain" {
  description = "Custom domain registered on the frontend Storage account (validated via an asverify CNAME), or null for none."
  type        = string
  default     = null

  validation {
    condition     = var.frontend_custom_domain == null || !can(regex("^https?://|/", var.frontend_custom_domain))
    error_message = "frontend_custom_domain must be a bare host name without scheme or path."
  }
}

variable "academiccloud_secret_name" {
  description = "Name of the pre-created AcademicCloud API key secret in Key Vault."
  type        = string
  default     = "academiccloud-api-key"
}

variable "academiccloud_base_url" {
  description = "AcademicCloud OpenAI-compatible API base URL."
  type        = string
  default     = "https://chat-ai.academiccloud.de/v1"
}

variable "academiccloud_model" {
  description = "AcademicCloud model used by the backend."
  type        = string
  default     = "qwen3-30b-a3b-instruct-2507"
}

variable "daily_global_actions" {
  description = "Process-local service-wide daily action allowance."
  type        = number
  default     = 150
}

variable "daily_user_actions" {
  description = "Process-local per-client daily action allowance."
  type        = number
  default     = 60
}

variable "tags" {
  description = "Additional tags merged onto all supported resources."
  type        = map(string)
  default     = {}
}
