# Variables for (π)NAD Infrastructure

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "pinad-project"
}

variable "region" {
  description = "Google Cloud Region (Tier 1 for cost optimization)"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "cloud_run_service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "pinad-api"
}

variable "cloud_run_container_image" {
  description = "Container image for Cloud Run"
  type        = string
  default     = "gcr.io/pinad-project/pinad-api:latest"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 100
}

variable "cloud_run_min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "cloud_run_cpu" {
  description = "CPU allocation for Cloud Run"
  type        = string
  default     = "1000m"
}

variable "cloud_run_memory" {
  description = "Memory allocation for Cloud Run"
  type        = string
  default     = "512Mi"
}

variable "cloud_run_concurrency" {
  description = "Maximum concurrent requests per instance"
  type        = number
  default     = 80
}

variable "cloud_run_timeout" {
  description = "Request timeout in seconds"
  type        = number
  default     = 300
}

variable "enable_cloud_run_autoscaling" {
  description = "Enable autoscaling for Cloud Run"
  type        = bool
  default     = true
}

variable "kms_key_ring_name" {
  description = "Cloud KMS Key Ring name"
  type        = string
  default     = "pinad-keyring"
}

variable "kms_crypto_key_name" {
  description = "Cloud KMS Crypto Key name"
  type        = string
  default     = "pinad-crypto-key"
}

variable "kms_key_rotation_period" {
  description = "KMS key rotation period"
  type        = string
  default     = "7776000s" # 90 days
}

variable "secret_manager_secrets" {
  description = "List of secrets to create in Secret Manager"
  type = list(object({
    name        = string
    secret_data = string
  }))
  default = [
    {
      name        = "firebase-admin-sdk"
      secret_data = "REPLACE_WITH_ACTUAL_SECRET"
    },
    {
      name        = "database-connection-string"
      secret_data = "REPLACE_WITH_ACTUAL_SECRET"
    },
    {
      name        = "oauth-client-secret"
      secret_data = "REPLACE_WITH_ACTUAL_SECRET"
    }
  ]
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable Cloud Logging"
  type        = bool
  default     = true
}

variable "enable_trace" {
  description = "Enable Cloud Trace"
  type        = bool
  default     = true
}

variable "enable_error_reporting" {
  description = "Enable Cloud Error Reporting"
  type        = bool
  default     = true
}

variable "notification_channels" {
  description = "Notification channels for alerts"
  type = list(object({
    display_name = string
    type        = string
    email       = string
  }))
  default = [
    {
      display_name = "pinad-alerts"
      type        = "email"
      email       = "alerts@pinad.com"
    }
  ]
}

variable "enable_multi_tenancy" {
  description = "Enable multi-tenancy"
  type        = bool
  default     = true
}

variable "tenant_isolation_level" {
  description = "Tenant isolation level (shared_schema, separate_schema, separate_database)"
  type        = string
  default     = "separate_schema"
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

variable "dr_enabled" {
  description = "Enable disaster recovery"
  type        = bool
  default     = true
}

variable "dr_rto_seconds" {
  description = "Recovery Time Objective in seconds"
  type        = number
  default     = 3600 # 1 hour
}

variable "dr_rpo_seconds" {
  description = "Recovery Point Objective in seconds"
  type        = number
  default     = 300 # 5 minutes
}

variable "compliance_standards" {
  description = "Compliance standards to enforce"
  type        = list(string)
  default     = ["PCI-DSS", "GDPR"]
}

# Additional Disaster Recovery Variables
variable "dr_secondary_region" {
  description = "Secondary region for disaster recovery"
  type        = string
  default     = "us-east1"
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 90
}

# Additional Compliance Variables
variable "enable_compliance" {
  description = "Enable compliance controls"
  type        = bool
  default     = true
}

variable "data_residency_region" {
  description = "Region for data residency compliance"
  type        = string
  default     = "us-central1"
}

variable "audit_log_retention_days" {
  description = "Number of days to retain audit logs for compliance"
  type        = number
  default     = 365
}

# Testing Variables
variable "enable_testing" {
  description = "Enable testing infrastructure"
  type        = bool
  default     = true
}

variable "test_environment" {
  description = "Test environment name"
  type        = string
  default     = "test"
}

variable "enable_e2e_testing" {
  description = "Enable end-to-end testing infrastructure"
  type        = bool
  default     = true
}

# Cost Optimization Variables
variable "enable_cost_optimization" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

variable "cost_budget_alert_threshold" {
  description = "Budget alert threshold in USD"
  type        = number
  default     = 1000
}

variable "enable_cpu_throttling" {
  description = "Enable CPU throttling for cost optimization"
  type        = bool
  default     = true
}

variable "enable_request_concurrency" {
  description = "Enable request concurrency for cost optimization"
  type        = bool
  default     = true
}
