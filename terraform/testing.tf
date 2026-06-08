# Testing Infrastructure for (π)NAD
# Supports unit, integration, and end-to-end testing

# Create test environment project
resource "google_project" "test_project" {
  count = var.enable_testing ? 1 : 0
  
  project_id      = "pinad-test"
  name            = "pinad-test"
  billing_account = var.billing_account_id
  
  labels = {
    environment = "test"
    managed-by  = "terraform"
  }
}

# Create test Cloud Run service
resource "google_cloud_run_v2_service" "pinad_api_test" {
  count = var.enable_testing ? 1 : 0
  
  name     = "${var.cloud_run_service_name}-test"
  location = var.region
  project  = google_project.test_project[0].project_id
  
  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    
    containers {
      image = var.cloud_run_container_image
      
      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
        cpu_idle = true
      }
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "PROJECT_ID"
        value = google_project.test_project[0].project_id
      }
      
      env {
        name  = "ENVIRONMENT"
        value = "test"
      }
      
      env {
        name  = "REGION"
        value = var.region
      }
      
      env {
        name  = "ENABLE_MULTI_TENANCY"
        value = "true"
      }
      
      env {
        name  = "TENANT_ISOLATION_LEVEL"
        value = "separate_schema"
      }
    }
    
    timeout_seconds = 300
    
    service_account = google_service_account.cloud_run_sa.email
    
    max_instance_request_concurrency = 80
  }
  
  ingress = "INGRESS_TRAFFIC_ALL"
  
  traffic {
    percent = 100
    latest_revision = true
  }
}

# Create test Cloud Build trigger for unit tests
resource "google_cloudbuild_trigger" "unit_test_trigger" {
  count = var.enable_testing ? 1 : 0
  
  name        = "unit-test-trigger"
  description = "Trigger for unit tests"
  project     = google_project.test_project[0].project_id
  
  github {
    owner = "YOUR_GITHUB_OWNER"
    name  = "YOUR_GITHUB_REPO"
    push {
      branch = "feature/*"
    }
  }
  
  build {
    steps {
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-t", "gcr.io/${google_project.test_project[0].project_id}/${var.cloud_run_service_name}:test", "."]
      dir  = "pinad_app"
    }
    
    steps {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${google_project.test_project[0].project_id}/${var.cloud_run_service_name}:test"]
    }
    
    steps {
      name = "gcr.io/cloud-builders/docker"
      args = ["run", "--rm", "-v", "${PWD}:/app", "-w", "/app", "google/dart:latest", "dart", "test", "--coverage"]
      dir  = "pinad_app"
    }
    
    steps {
      name = "gcr.io/cloud-builders/gsutil"
      args = ["cp", "-r", "pinad_app/coverage", "gs://${google_project.test_project[0].project_id}-test-coverage/"]
    }
    
    timeout = "1800s"
  }
}

# Create test Cloud Build trigger for integration tests
resource "google_cloudbuild_trigger" "integration_test_trigger" {
  count = var.enable_testing ? 1 : 0
  
  name        = "integration-test-trigger"
  description = "Trigger for integration tests"
  project     = google_project.test_project[0].project_id
  
  github {
    owner = "YOUR_GITHUB_OWNER"
    name  = "YOUR_GITHUB_REPO"
    push {
      branch = "develop"
    }
  }
  
  build {
    steps {
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-t", "gcr.io/${google_project.test_project[0].project_id}/${var.cloud_run_service_name}:test", "."]
      dir  = "pinad_app"
    }
    
    steps {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${google_project.test_project[0].project_id}/${var.cloud_run_service_name}:test"]
    }
    
    steps {
      name = "gcr.io/cloud-builders/gcloud"
      args = [
        "run", "deploy", "${var.cloud_run_service_name}-test",
        "--image", "gcr.io/${google_project.test_project[0].project_id}/${var.cloud_run_service_name}:test",
        "--platform", "managed",
        "--region", var.region,
        "--allow-unauthenticated",
        "--set-env-vars", "PROJECT_ID=${google_project.test_project[0].project_id},ENVIRONMENT=test"
      ]
    }
    
    steps {
      name = "gcr.io/cloud-builders/curl"
      args = ["-X", "POST", "https://${var.region}-${google_project.test_project[0].project_id}.cloudfunctions.net/runIntegrationTests"]
    }
    
    timeout = "1800s"
  }
}

# Create E2E test infrastructure
resource "google_cloud_scheduler_job" "e2e_test_scheduler" {
  count = var.enable_e2e_testing ? 1 : 0
  
  name        = "e2e-test-scheduler"
  description = "Scheduled E2E tests"
  project     = google_project.test_project[0].project_id
  region      = var.region
  
  schedule = "0 6 * * *" # Daily at 6 AM
  
  time_zone = "America/New_York"
  
  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-${google_project.test_project[0].project_id}.cloudfunctions.net/runE2ETests"
    oidc_token {
      service_account_email = google_service_account.cloud_build_sa.email
    }
  }
}

# Create test database for integration tests
resource "google_sql_database" "test_database" {
  count = var.enable_testing ? 1 : 0
  
  name     = "pinad_test_db"
  instance = google_sql_database_instance.test_instance[0].name
  project  = google_project.test_project[0].project_id
}

# Create test SQL instance for integration tests
resource "google_sql_database_instance" "test_instance" {
  count = var.enable_testing ? 1 : 0
  
  name             = "pinad-test-instance"
  project          = google_project.test_project[0].project_id
  region           = var.region
  database_version = "MYSQL_8_0"
  
  settings {
    tier = "db-f1-micro"
    
    backup_configuration {
      enabled = true
    }
    
    ip_configuration {
      ipv4_enabled = true
      
      authorized_networks {
        name  = "test-network"
        value = "0.0.0.0/0"
      }
    }
    
    location_preference {
      zone = var.zone
    }
    
    database_flags {
      name  = "general_log"
      value = "on"
    }
  }
  
  deletion_protection = false
}

# Create test storage bucket for test data
resource "google_storage_bucket" "test_data_bucket" {
  count = var.enable_testing ? 1 : 0
  
  name          = "pinad-test-data"
  location      = var.region
  force_destroy = true
  uniform_bucket_level_access = true
  
  labels = {
    environment = "test"
    purpose     = "testing"
    managed-by  = "terraform"
  }
}

# Create test Firestore database
resource "google_firestore_database" "test_firestore" {
  count = var.enable_testing ? 1 : 0
  
  project        = google_project.test_project[0].project_id
  name           = "(default)"
  location_id    = var.region
  type           = "FIRESTORE_NATIVE"
  
  concurrency_mode = "OPTIMISTIC"
  
  labels = {
    environment = "test"
    purpose     = "testing"
    managed-by  = "terraform"
  }
}

# Create test monitoring dashboard
resource "google_monitoring_dashboard" "test_dashboard" {
  count = var.enable_testing ? 1 : 0
  
  dashboard_json = jsonencode({
    displayName = "Test Environment Dashboard"
    gridLayout = {
      columns = 2
      widgets = [
        {
          title = "Test Execution Time"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_function\" AND resource.labels.function_name=\"runE2ETests\""
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
          title = "Test Pass Rate"
          scorecard = {
            dataView = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_function\" AND metric.type=\"custom.googleapis.com/test_pass_rate\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }
          }
        }
        {
          title = "Test Coverage"
          scorecard = {
            dataView = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_function\" AND metric.type=\"custom.googleapis.com/test_coverage\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }
          }
        }
        {
          title = "Test Failures"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_function\" AND metric.type=\"custom.googleapis.com/test_failures\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_COUNT"
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

# Create test alert policy
resource "google_monitoring_alert_policy" "test_failure_alert" {
  count = var.enable_testing ? 1 : 0
  
  display_name = "Test Failure Alert"
  project      = google_project.test_project[0].project_id
  
  conditions {
    display_name = "Test failure rate > 10%"
    
    condition_threshold {
      filter = "resource.type=\"cloud_function\" AND metric.type=\"custom.googleapis.com/test_failures\""
      
      comparison = "COMPARISON_GT"
      threshold_value = 10
      duration        = "300s"
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner = "ALIGN_COUNT"
      }
    }
  }
  
  alert_strategy {
    notification_rate_limit {
      period = "3600s"
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.test_alerts[0].name
  ]
  
  enabled = true
}

# Create test notification channel
resource "google_monitoring_notification_channel" "test_alerts" {
  count = var.enable_testing ? 1 : 0
  
  display_name = "Test Alerts"
  type         = "email"
  
  labels = {
    email_address = "test@pinad.com"
  }
  
  project = google_project.test_project[0].project_id
}

# Grant IAM permissions for test project
resource "google_project_iam_member" "test_project_iam" {
  count = var.enable_testing ? 1 : 0
  
  project = google_project.test_project[0].project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}

# Create test service account
resource "google_service_account" "test_sa" {
  count = var.enable_testing ? 1 : 0
  
  account_id   = "pinad-test-sa"
  display_name = "Test Service Account"
  project      = google_project.test_project[0].project_id
}

# Grant roles to test service account
resource "google_project_iam_member" "test_sa_roles" {
  count = var.enable_testing ? 3 : 0
  
  project = google_project.test_project[0].project_id
  role    = [
    "roles/cloudfunctions.invoker",
    "roles/datastore.user",
    "roles/storage.objectAdmin"
  ][count.index]
  member  = "serviceAccount:${google_service_account.test_sa[0].email}"
}
