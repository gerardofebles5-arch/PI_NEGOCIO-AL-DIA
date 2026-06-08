# Disaster Recovery and Backup Strategies for (π)NAD

# Create backup bucket for Firestore exports
resource "google_storage_bucket" "firestore_backup_bucket" {
  count = var.dr_enabled ? 1 : 0
  
  name          = "pinad-firestore-backups"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      age = var.backup_retention_days
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "backup"
    data-source = "firestore"
  }
}

# Create backup bucket for Cloud SQL exports
resource "google_storage_bucket" "cloudsql_backup_bucket" {
  count = var.dr_enabled ? 1 : 0
  
  name          = "pinad-cloudsql-backups"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      age = var.backup_retention_days
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "backup"
    data-source = "cloudsql"
  }
}

# Create backup bucket for multi-tenant data
resource "google_storage_bucket" "multitenant_backup_bucket" {
  count = var.dr_enabled && var.enable_multi_tenancy ? 1 : 0
  
  name          = "pinad-multitenant-backups"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      age = var.backup_retention_days
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "backup"
    data-source = "multitenant"
  }
}

# Create Cloud Scheduler job for Firestore backups
resource "google_cloud_scheduler_job" "firestore_backup_job" {
  count = var.dr_enabled ? 1 : 0
  
  name        = "firestore-backup-scheduler"
  description = "Scheduled Firestore backups"
  project     = var.project_id
  region      = var.region
  
  schedule = "0 2 * * *" # Daily at 2 AM
  
  time_zone = "America/New_York"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-${var.project_id}.cloudfunctions.net/scheduleFirestoreBackup"
    oidc_token {
      service_account_email = google_service_account.cloud_build_sa.email
    }
  }
}

# Create Cloud Scheduler job for Cloud SQL backups
resource "google_cloud_scheduler_job" "cloudsql_backup_job" {
  count = var.dr_enabled ? 1 : 0
  
  name        = "cloudsql-backup-scheduler"
  description = "Scheduled Cloud SQL backups"
  project     = var.project_id
  region      = var.region
  
  schedule = "0 3 * * *" # Daily at 3 AM
  
  time_zone = "America/New_York"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-${var.project_id}.cloudfunctions.net/scheduleCloudSQLBackup"
    oidc_token {
      service_account_email = google_service_account.cloud_build_sa.email
    }
  }
}

# Create Cloud Scheduler job for multi-tenant backups
resource "google_cloud_scheduler_job" "multitenant_backup_job" {
  count = var.dr_enabled && var.enable_multi_tenancy ? 1 : 0
  
  name        = "multitenant-backup-scheduler"
  description = "Scheduled multi-tenant backups"
  project     = var.project_id
  region      = var.region
  
  schedule = "0 4 * * *" # Daily at 4 AM
  
  time_zone = "America/New_York"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-${var.project_id}.cloudfunctions.net/scheduleMultiTenantBackup"
    oidc_token {
      service_account_email = google_service_account.cloud_build_sa.email
    }
  }
}

# Create secondary region for disaster recovery
resource "google_compute_region" "dr_secondary_region" {
  count = var.dr_enabled ? 1 : 0
  
  name   = "dr-secondary-region"
  region = "us-east1" # Secondary region for DR
}

# Create secondary Cloud Run service for DR
resource "google_cloud_run_v2_service" "pinad_api_dr" {
  count = var.dr_enabled ? 1 : 0
  
  name     = "${var.cloud_run_service_name}-dr"
  location = "us-east1" # Secondary region
  project  = var.project_id
  
  template {
    scaling {
      min_instance_count = 0
      max_instance_count = var.cloud_run_max_instances
    }
    
    containers {
      image = var.cloud_run_container_image
      
      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
        cpu_idle = true
      }
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "ENVIRONMENT"
        value = "${var.environment}-dr"
      }
      
      env {
        name  = "REGION"
        value = "us-east1"
      }
      
      env {
        name  = "ENABLE_MULTI_TENANCY"
        value = var.enable_multi_tenancy ? "true" : "false"
      }
      
      env {
        name  = "TENANT_ISOLATION_LEVEL"
        value = var.tenant_isolation_level
      }
    }
    
    timeout_seconds = var.cloud_run_timeout
    
    service_account = google_service_account.cloud_run_sa.email
    
    max_instance_request_concurrency = var.cloud_run_concurrency
  }
  
  ingress = "INGRESS_TRAFFIC_ALL"
  
  traffic {
    percent = 0 # No traffic by default, only for DR
    latest_revision = true
  }
}

# Create DNS record for DR failover
resource "google_dns_record_set" "dr_failover" {
  count = var.dr_enabled ? 1 : 0
  
  name = "pinad-api"
  type = "A"
  ttl  = 300
  
  managed_zone = "pinad-dns-zone"
  
  rrdatas = [
    # Primary region IP (to be configured)
    "1.2.3.4",
  ]
}

# Create Cloud Function for DR failover
resource "google_cloudfunctions_function" "dr_failover_function" {
  count = var.dr_enabled ? 1 : 0
  
  name        = "dr-failover"
  description = "Function to trigger DR failover"
  runtime     = "nodejs18"
  
  source_archive_bucket = google_storage_bucket.terraform_state.name
  source_archive_object = google_storage_bucket_object.dr_failover_source[0].name
  
  entry_point = "drFailover"
  
  trigger_http = true
  
  environment_variables = {
    PRIMARY_REGION = var.region
    SECONDARY_REGION = "us-east1"
    SERVICE_NAME = var.cloud_run_service_name
  }
  
  service_account_email = google_service_account.cloud_build_sa.email
}

# Create source archive for DR failover function
resource "google_storage_bucket_object" "dr_failover_source" {
  count = var.dr_enabled ? 1 : 0
  
  name   = "dr-failover-source.zip"
  bucket = google_storage_bucket.terraform_state.name
  source = "${path.module}/dr_failover_function.zip"
}

# Create Cloud Function for DR health check
resource "google_cloudfunctions_function" "dr_health_check" {
  count = var.dr_enabled ? 1 : 0
  
  name        = "dr-health-check"
  description = "Function to check health of DR environment"
  runtime     = "nodejs18"
  
  source_archive_bucket = google_storage_bucket.terraform_state.name
  source_archive_object = google_storage_bucket_object.dr_health_check_source[0].name
  
  entry_point = "drHealthCheck"
  
  trigger_http = true
  
  environment_variables = {
    PRIMARY_REGION = var.region
    SECONDARY_REGION = "us-east1"
    SERVICE_NAME = var.cloud_run_service_name
  }
  
  service_account_email = google_service_account.cloud_build_sa.email
}

# Create source archive for DR health check function
resource "google_storage_bucket_object" "dr_health_check_source" {
  count = var.dr_enabled ? 1 : 0
  
  name   = "dr-health-check-source.zip"
  bucket = google_storage_bucket.terraform_state.name
  source = "${path.module}/dr_health_check_function.zip"
}

# Create Cloud Scheduler job for DR health checks
resource "google_cloud_scheduler_job" "dr_health_check_job" {
  count = var.dr_enabled ? 1 : 0
  
  name        = "dr-health-check-scheduler"
  description = "Scheduled DR health checks"
  project     = var.project_id
  region      = var.region
  
  schedule = "*/15 * * * *" # Every 15 minutes
  
  time_zone = "America/New_York"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-${var.project_id}.cloudfunctions.net/dr-health-check"
    oidc_token {
      service_account_email = google_service_account.cloud_build_sa.email
    }
  }
}

# Grant Cloud Build service account access to backup buckets
resource "google_storage_bucket_iam_member" "backup_bucket_access" {
  count = var.dr_enabled ? 3 : 0
  
  bucket = [
    google_storage_bucket.firestore_backup_bucket[0].name,
    google_storage_bucket.cloudsql_backup_bucket[0].name,
    var.enable_multi_tenancy ? google_storage_bucket.multitenant_backup_bucket[0].name : null,
  ][count.index]
  
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}
