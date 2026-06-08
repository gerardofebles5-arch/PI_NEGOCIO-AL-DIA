# Secret Manager configuration for (π)NAD

# Create Secret Manager secrets
resource "google_secret_manager_secret" "pinad_secrets" {
  for_each = {
    for secret in var.secret_manager_secrets : secret.name => secret
  }
  
  secret_id = each.value.name
  project   = var.project_id
  
  replication {
    automatic = true
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

# Create secret versions
resource "google_secret_manager_secret_version" "pinad_secret_versions" {
  for_each = {
    for secret in var.secret_manager_secrets : secret.name => secret
  }
  
  secret      = google_secret_manager_secret.pinad_secrets[each.key].id
  secret_data = each.value.secret_data
}

# Grant Cloud Run service account access to secrets
resource "google_secret_manager_secret_iam_member" "secret_access" {
  for_each = {
    for secret in var.secret_manager_secrets : secret.name => secret
  }
  
  project   = var.project_id
  secret_id = google_secret_manager_secret.pinad_secrets[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Cloud Build service account access to secrets
resource "google_secret_manager_secret_iam_member" "secret_access_build" {
  for_each = {
    for secret in var.secret_manager_secrets : secret.name => secret
  }
  
  project   = var.project_id
  secret_id = google_secret_manager_secret.pinad_secrets[each.key].secret_id
  role      = "roles/secretmanager.admin"
  member    = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}

# Create secret for OAuth2 refresh token rotation
resource "google_secret_manager_secret" "oauth_refresh_token_rotation" {
  secret_id = "oauth-refresh-token-rotation"
  project   = var.project_id
  
  replication {
    automatic = true
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "oauth2"
  }
}

# Create secret for multi-tenancy tenant IDs
resource "google_secret_manager_secret" "multi_tenant_ids" {
  count      = var.enable_multi_tenancy ? 1 : 0
  secret_id  = "multi-tenant-ids"
  project    = var.project_id
  
  replication {
    automatic = true
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "multi-tenancy"
  }
}

# Create secret for database connection strings per tenant
resource "google_secret_manager_secret" "tenant_database_connections" {
  count      = var.enable_multi_tenancy ? 1 : 0
  secret_id  = "tenant-database-connections"
  project    = var.project_id
  
  replication {
    automatic = true
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "multi-tenancy"
  }
}
