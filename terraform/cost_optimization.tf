# Cost Optimization for (π)NAD
# Optimizes Cloud Run costs with budget alerts, resource limits, and scaling policies

# Create budget for cost monitoring
resource "google_billing_budget" "pinad_budget" {
  count = var.enable_cost_optimization ? 1 : 0
  
  billing_account = var.billing_account_id
  display_name    = "pinad-budget"
  
  budget_filter {
    projects = ["projects/${var.project_id}"]
  }
  
  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.cost_budget_alert_threshold
    }
  }
  
  threshold_rules {
    threshold_percent = 50.0
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 75.0
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 90.0
    spend_basis       = "CURRENT_SPEND"
  }
  
  threshold_rules {
    threshold_percent = 100.0
    spend_basis       = "CURRENT_SPEND"
  }
  
  all_updates_rule {
    pubsub_topic = "projects/${var.project_id}/topics/budget-alerts"
    schema_version = "1.0"
  }
}

# Create Pub/Sub topic for budget alerts
resource "google_pubsub_topic" "budget_alerts" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name = "budget-alerts"
  project = var.project_id
  
  labels = {
    environment = var.environment
    purpose     = "cost-optimization"
    managed-by  = "terraform"
  }
}

# Create Cloud Function to handle budget alerts
resource "google_cloudfunctions_function" "budget_alert_handler" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name        = "budget-alert-handler"
  description = "Function to handle budget alerts"
  runtime     = "nodejs18"
  
  source_archive_bucket = google_storage_bucket.terraform_state.name
  source_archive_object = google_storage_bucket_object.budget_alert_handler_source[0].name
  
  entry_point = "budgetAlertHandler"
  
  trigger_http = true
  
  environment_variables = {
    PROJECT_ID = var.project_id
    BUDGET_THRESHOLD = var.cost_budget_alert_threshold
  }
  
  service_account_email = google_service_account.cloud_build_sa.email
}

# Create source archive for budget alert handler
resource "google_storage_bucket_object" "budget_alert_handler_source" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name   = "budget-alert-handler-source.zip"
  bucket = google_storage_bucket.terraform_state.name
  source = "${path.module}/budget_alert_handler_function.zip"
}

# Create Pub/Sub subscription for budget alerts
resource "google_pubsub_subscription" "budget_alerts_subscription" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name  = "budget-alerts-subscription"
  topic = google_pubsub_topic.budget_alerts[0].name
  
  push_config {
    push_endpoint = "https://${var.region}-${var.project_id}.cloudfunctions.net/budget-alert-handler"
    oidc_token {
      service_account_email = google_service_account.cloud_build_sa.email
    }
  }
}

# Create cost optimization monitoring dashboard
resource "google_monitoring_dashboard" "cost_optimization_dashboard" {
  count = var.enable_cost_optimization ? 1 : 0
  
  dashboard_json = jsonencode({
    displayName = "Cost Optimization Dashboard"
    gridLayout = {
      columns = 2
      widgets = [
        {
          title = "Cloud Run Costs"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"billing.googleapis.com/billed_amount\""
                  aggregation = {
                    alignmentPeriod = "86400s"
                    perSeriesAligner = "ALIGN_SUM"
                  }
                }
              }
            }]
          }
        }
        {
          title = "Instance Utilization"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/instance_count\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
        {
          title = "Request Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_SUM"
                  }
                }
              }
            }]
          }
        }
        {
          title = "CPU Utilization"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/cpu/utilizations\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
        {
          title = "Memory Utilization"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/memory/utilizations\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
        {
          title = "Budget vs Actual Spend"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"billing.googleapis.com/billed_amount\""
                  aggregation = {
                    alignmentPeriod = "86400s"
                    perSeriesAligner = "ALIGN_SUM"
                  }
                }
              }
            }]
          }
        }
      ]
    }
  })
}

# Create cost alert policy
resource "google_monitoring_alert_policy" "cost_alert_policy" {
  count = var.enable_cost_optimization ? 1 : 0
  
  display_name = "Cost Alert Policy"
  project      = var.project_id
  
  conditions {
    display_name = "Daily cost exceeds threshold"
    
    condition_threshold {
      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"billing.googleapis.com/billed_amount\""
      
      comparison = "COMPARISON_GT"
      threshold_value = var.cost_budget_alert_threshold * 0.8 # 80% of budget
      duration        = "86400s" # 1 day
      
      aggregations {
        alignment_period     = "86400s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }
  
  alert_strategy {
    notification_rate_limit {
      period = "86400s"
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.cost_alerts[0].name
  ]
  
  enabled = true
}

# Create cost notification channel
resource "google_monitoring_notification_channel" "cost_alerts" {
  count = var.enable_cost_optimization ? 1 : 0
  
  display_name = "Cost Alerts"
  type         = "email"
  
  labels = {
    email_address = "finance@pinad.com"
  }
  
  project = var.project_id
}

# Update Cloud Run service with cost optimization settings
resource "google_cloud_run_v2_service" "pinad_api_cost_optimized" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name     = var.cloud_run_service_name
  location = var.region
  project  = var.project_id
  
  template {
    scaling {
      min_instance_count = var.cloud_run_min_instances
      max_instance_count = var.cloud_run_max_instances
    }
    
    containers {
      image = var.cloud_run_container_image
      
      resources {
        limits = {
          cpu    = var.cloud_run_cpu
          memory = var.cloud_run_memory
        }
        cpu_idle = var.enable_cpu_throttling
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
        value = var.environment
      }
      
      env {
        name  = "REGION"
        value = var.region
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
    
    max_instance_request_concurrency = var.enable_request_concurrency ? var.cloud_run_concurrency : 1
  }
  
  ingress = "INGRESS_TRAFFIC_ALL"
  
  traffic {
    percent = 100
    latest_revision = true
  }
}

# Create cost optimization scheduler for scaling down during off-peak hours
resource "google_cloud_scheduler_job" "cost_optimization_scheduler" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name        = "cost-optimization-scheduler"
  description = "Scheduler for cost optimization scaling"
  project     = var.project_id
  region      = var.region
  
  schedule = "0 0 * * *" # Daily at midnight
  
  time_zone = "America/New_York"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-${var.project_id}.cloudfunctions.net/costOptimizationScaler"
    oidc_token {
      service_account_email = google_service_account.cloud_build_sa.email
    }
  }
}

# Create Cloud Function for cost optimization scaling
resource "google_cloudfunctions_function" "cost_optimization_scaler" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name        = "cost-optimization-scaler"
  description = "Function to scale Cloud Run for cost optimization"
  runtime     = "nodejs18"
  
  source_archive_bucket = google_storage_bucket.terraform_state.name
  source_archive_object = google_storage_bucket_object.cost_optimization_scaler_source[0].name
  
  entry_point = "costOptimizationScaler"
  
  trigger_http = true
  
  environment_variables = {
    PROJECT_ID = var.project_id
    REGION = var.region
    SERVICE_NAME = var.cloud_run_service_name
    OFF_PEAK_MIN_INSTANCES = 0
    PEAK_MIN_INSTANCES = 1
    PEAK_START_HOUR = 9
    PEAK_END_HOUR = 17
  }
  
  service_account_email = google_service_account.cloud_build_sa.email
}

# Create source archive for cost optimization scaler
resource "google_storage_bucket_object" "cost_optimization_scaler_source" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name   = "cost-optimization-scaler-source.zip"
  bucket = google_storage_bucket.terraform_state.name
  source = "${path.module}/cost_optimization_scaler_function.zip"
}

# Create cost metrics export to BigQuery
resource "google_logging_project_sink" "cost_metrics_sink" {
  count = var.enable_cost_optimization ? 1 : 0
  
  name = "cost-metrics-sink"
  project = var.project_id
  
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/cost_metrics"
  
  filter = "resource.type=\"cloud_run_revision\" AND logName:\"logs/cloudaudit.googleapis.com\""
  
  unique_writer_identity = true
}

# Create BigQuery dataset for cost metrics
resource "google_bigquery_dataset" "cost_metrics" {
  count = var.enable_cost_optimization ? 1 : 0
  
  dataset_id = "cost_metrics"
  project    = var.project_id
  location   = var.region
  
  default_table_expiration_ms = 30 * 24 * 60 * 60 * 1000 # 30 days
  
  labels = {
    environment = var.environment
    purpose     = "cost-optimization"
    managed-by  = "terraform"
  }
  
  access {
    role = "roles/bigquery.dataViewer"
    user_by_email = "finance@pinad.com"
  }
  
  access {
    role = "roles/bigquery.dataEditor"
    user_by_email = "devops@pinad.com"
  }
}

# Grant IAM permissions for cost metrics sink
resource "google_project_iam_member" "cost_metrics_sink_iam" {
  count = var.enable_cost_optimization ? 1 : 0
  
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_logging_project_sink.cost_metrics_sink[0].writer_identity}"
}

# Create cost anomaly detection
resource "google_monitoring_alert_policy" "cost_anomaly_alert" {
  count = var.enable_cost_optimization ? 1 : 0
  
  display_name = "Cost Anomaly Alert"
  project      = var.project_id
  
  conditions {
    display_name = "Cost anomaly detected"
    
    condition_threshold {
      filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"billing.googleapis.com/billed_amount\""
      
      comparison = "COMPARISON_GT"
      threshold_value = 0 # Will be set dynamically
      duration        = "3600s" # 1 hour
      
      aggregations {
        alignment_period     = "3600s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  alert_strategy {
    auto_close {
      duration = "86400s"
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.cost_alerts[0].name
  ]
  
  enabled = true
}
