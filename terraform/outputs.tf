# Outputs for (π)NAD Infrastructure

output "project_id" {
  description = "Google Cloud Project ID"
  value       = var.project_id
}

output "region" {
  description = "Google Cloud Region"
  value       = var.region
}

output "environment" {
  description = "Environment"
  value       = var.environment
}

output "cloud_run_service_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.pinad_api[0].uri
}

output "cloud_run_service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.pinad_api[0].name
}

output "kms_key_name" {
  description = "Cloud KMS Crypto Key name"
  value       = google_kms_crypto_key.pinad_crypto_key[0].name
}

output "kms_key_ring_name" {
  description = "Cloud KMS Key Ring name"
  value       = google_kms_key_ring.pinad_keyring[0].name
}

output "secret_manager_secrets" {
  description = "Secret Manager secrets"
  value = {
    for secret in google_secret_manager_secret.pinad_secrets : secret.secret_id => secret.name
  }
}

output "monitoring_dashboard_url" {
  description = "Cloud Monitoring dashboard URL"
  value       = "https://console.cloud.google.com/monitoring/dashboards?project=${var.project_id}"
}

output "logging_view_url" {
  description = "Cloud Logging view URL"
  value       = "https://console.cloud.google.com/logging?project=${var.project_id}"
}

output "cloud_build_trigger_ids" {
  description = "Cloud Build trigger IDs"
  value       = google_cloudbuild_trigger.pinad_triggers[*].id
}

output "terraform_state_bucket" {
  description = "Terraform state bucket name"
  value       = "pinad-terraform-state"
}
