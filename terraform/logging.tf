# Cloud Logging configuration for (π)NAD

# Create log sink for Cloud Run logs
resource "google_logging_project_sink" "cloud_run_logs" {
  count = var.enable_logging ? 1 : 0
  
  name                   = "pinad-cloud-run-logs-sink"
  project                = var.project_id
  destination            = "bigquery.googleapis.com/projects/${var.project_id}/datasets/pinad_logs"
  filter                 = "resource.type=\"cloud_run_revision\""
  unique_writer_identity = true
}

# Create BigQuery dataset for logs
resource "google_bigquery_dataset" "pinad_logs" {
  count = var.enable_logging ? 1 : 0
  
  dataset_id  = "pinad_logs"
  project     = var.project_id
  location    = var.region
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "logging"
  }
  
  default_table_expiration_ms = 7776000000 # 90 days
}

# Grant logging service account access to BigQuery dataset
resource "google_bigquery_dataset_iam_member" "logging_bigquery_access" {
  count = var.enable_logging ? 1 : 0
  
  project    = google_bigquery_dataset.pinad_logs[0].project
  dataset_id = google_bigquery_dataset.pinad_logs[0].dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = google_logging_project_sink.cloud_run_logs[0].writer_identity
}

# Create log sink for audit logs
resource "google_logging_project_sink" "audit_logs" {
  count = var.enable_logging ? 1 : 0
  
  name                   = "pinad-audit-logs-sink"
  project                = var.project_id
  destination            = "bigquery.googleapis.com/projects/${var.project_id}/datasets/pinad_audit_logs"
  filter                 = "logName:\"logs/cloudaudit.googleapis.com\""
  unique_writer_identity = true
}

# Create BigQuery dataset for audit logs
resource "google_bigquery_dataset" "pinad_audit_logs" {
  count = var.enable_logging ? 1 : 0
  
  dataset_id  = "pinad_audit_logs"
  project     = var.project_id
  location    = var.region
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "audit-logging"
  }
  
  default_table_expiration_ms = 7776000000 # 90 days
}

# Grant logging service account access to audit logs dataset
resource "google_bigquery_dataset_iam_member" "audit_logging_bigquery_access" {
  count = var.enable_logging ? 1 : 0
  
  project    = google_bigquery_dataset.pinad_audit_logs[0].project
  dataset_id = google_bigquery_dataset.pinad_audit_logs[0].dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = google_logging_project_sink.audit_logs[0].writer_identity
}

# Create log sink for multi-tenant logs
resource "google_logging_project_sink" "multi_tenant_logs" {
  count = var.enable_logging && var.enable_multi_tenancy ? 1 : 0
  
  name                   = "pinad-multi-tenant-logs-sink"
  project                = var.project_id
  destination            = "bigquery.googleapis.com/projects/${var.project_id}/datasets/pinad_multi_tenant_logs"
  filter                 = "resource.type=\"cloud_run_revision\" AND labels.tenant_id:*"
  unique_writer_identity = true
}

# Create BigQuery dataset for multi-tenant logs
resource "google_bigquery_dataset" "pinad_multi_tenant_logs" {
  count = var.enable_logging && var.enable_multi_tenancy ? 1 : 0
  
  dataset_id  = "pinad_multi_tenant_logs"
  project     = var.project_id
  location    = var.region
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "multi-tenant-logging"
  }
  
  default_table_expiration_ms = 7776000000 # 90 days
}

# Grant logging service account access to multi-tenant logs dataset
resource "google_bigquery_dataset_iam_member" "multi_tenant_logging_bigquery_access" {
  count = var.enable_logging && var.enable_multi_tenancy ? 1 : 0
  
  project    = google_bigquery_dataset.pinad_multi_tenant_logs[0].project
  dataset_id = google_bigquery_dataset.pinad_multi_tenant_logs[0].dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = google_logging_project_sink.multi_tenant_logs[0].writer_identity
}

# Create log-based metric for error rate
resource "google_logging_metric" "error_rate_metric" {
  count = var.enable_logging ? 1 : 0
  
  name   = "pinad-error-rate"
  project = var.project_id
  
  filter = "resource.type=\"cloud_run_revision\" AND severity>=ERROR"
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    display_name = "Error Rate"
  }
  
  label_extractors = {
    service_name = "resource.labels.service_name"
    revision_name = "resource.labels.revision_name"
  }
}

# Create log-based metric for request count
resource "google_logging_metric" "request_count_metric" {
  count = var.enable_logging ? 1 : 0
  
  name   = "pinad-request-count"
  project = var.project_id
  
  filter = "resource.type=\"cloud_run_revision\" AND httpRequest.requestMethod:*"
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    display_name = "Request Count"
  }
  
  label_extractors = {
    service_name = "resource.labels.service_name"
    revision_name = "resource.labels.revision_name"
    method = "httpRequest.requestMethod"
  }
}

# Create log-based metric for tenant-specific requests
resource "google_logging_metric" "tenant_request_metric" {
  count = var.enable_logging && var.enable_multi_tenancy ? 1 : 0
  
  name   = "pinad-tenant-request-count"
  project = var.project_id
  
  filter = "resource.type=\"cloud_run_revision\" AND labels.tenant_id:*"
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    display_name = "Tenant Request Count"
  }
  
  label_extractors = {
    service_name = "resource.labels.service_name"
    tenant_id = "labels.tenant_id"
  }
}

# Create log view for Cloud Run logs
resource "google_logging_view" "cloud_run_view" {
  count = var.enable_logging ? 1 : 0
  
  name   = "pinad-cloud-run-view"
  project = var.project_id
  
  filter = "resource.type=\"cloud_run_revision\""
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

# Create log view for audit logs
resource "google_logging_view" "audit_view" {
  count = var.enable_logging ? 1 : 0
  
  name   = "pinad-audit-view"
  project = var.project_id
  
  filter = "logName:\"logs/cloudaudit.googleapis.com\""
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
  }
}
