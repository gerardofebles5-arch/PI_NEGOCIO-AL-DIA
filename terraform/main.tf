# Main configuration for (π)NAD Infrastructure

# Enable required Google Cloud APIs
resource "google_project_service" "enable_apis" {
  project = var.project_id
  
  services = [
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudkms.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudmonitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "clouderrorreporting.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "firestore.googleapis.com",
    "pubsub.googleapis.com",
    "sourcerepo.googleapis.com",
    "appengine.googleapis.com",
  ]
  
  disable_on_destroy = false
}

# Create Terraform state bucket
resource "google_storage_bucket" "terraform_state" {
  name          = "pinad-terraform-state"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

# Create service account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "pinad-cloud-run-sa"
  display_name = "(π)NAD Cloud Run Service Account"
  project      = var.project_id
}

# Grant Cloud Run service account necessary permissions
resource "google_project_iam_member" "cloud_run_sa_roles" {
  for_each = toset([
    "roles/secretmanager.secretAccessor",
    "roles/cloudkms.cryptoKeyDecrypter",
    "roles/cloudkms.cryptoKeyEncrypter",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent",
    "roles/errorreporting.writer",
    "roles/datastore.user",
    "roles/bigquery.dataEditor",
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Create service account for Cloud Build
resource "google_service_account" "cloud_build_sa" {
  account_id   = "pinad-cloud-build-sa"
  display_name = "(π)NAD Cloud Build Service Account"
  project      = var.project_id
}

# Grant Cloud Build service account necessary permissions
resource "google_project_iam_member" "cloud_build_sa_roles" {
  for_each = toset([
    "roles/cloudbuild.builds.builder",
    "roles/run.admin",
    "roles/secretmanager.admin",
    "roles/cloudkms.admin",
    "roles/iam.serviceAccountUser",
    "roles/storage.admin",
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}
