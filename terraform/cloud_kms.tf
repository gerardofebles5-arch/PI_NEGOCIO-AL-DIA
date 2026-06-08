# Cloud KMS configuration for (π)NAD

# Create Cloud KMS Key Ring
resource "google_kms_key_ring" "pinad_keyring" {
  name     = var.kms_key_ring_name
  location = var.region
  project  = var.project_id
}

# Create Cloud KMS Crypto Key
resource "google_kms_crypto_key" "pinad_crypto_key" {
  name            = var.kms_crypto_key_name
  key_ring        = google_kms_key_ring.pinad_keyring.id
  rotation_period = var.kms_key_rotation_period
  purpose         = "ENCRYPT_DECRYPT"
  
  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = "SOFTWARE"
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
  }
  
  lifecycle {
    prevent_destroy = true
  }
}

# Create Cloud KMS Crypto Key for OAuth2 tokens
resource "google_kms_crypto_key" "oauth_tokens_key" {
  name            = "oauth-tokens-key"
  key_ring        = google_kms_key_ring.pinad_keyring.id
  rotation_period = var.kms_key_rotation_period
  purpose         = "ENCRYPT_DECRYPT"
  
  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = "SOFTWARE"
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "oauth2"
  }
}

# Create Cloud KMS Crypto Key for multi-tenancy data
resource "google_kms_crypto_key" "multi_tenant_data_key" {
  count           = var.enable_multi_tenancy ? 1 : 0
  name            = "multi-tenant-data-key"
  key_ring        = google_kms_key_ring.pinad_keyring.id
  rotation_period = var.kms_key_rotation_period
  purpose         = "ENCRYPT_DECRYPT"
  
  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = "SOFTWARE"
  }
  
  labels = {
    environment = var.environment
    managed-by  = "terraform"
    purpose     = "multi-tenancy"
  }
}

# Grant Cloud Run service account access to KMS keys
resource "google_kms_crypto_key_iam_member" "cloud_run_kms_access" {
  for_each = toset([
    google_kms_crypto_key.pinad_crypto_key.id,
    google_kms_crypto_key.oauth_tokens_key.id,
  ])
  
  crypto_key_id = each.value
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Cloud Run service account access to multi-tenant data key
resource "google_kms_crypto_key_iam_member" "cloud_run_multi_tenant_kms_access" {
  count         = var.enable_multi_tenancy ? 1 : 0
  crypto_key_id = google_kms_crypto_key.multi_tenant_data_key[0].id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Grant Cloud Build service account access to KMS keys
resource "google_kms_crypto_key_iam_member" "cloud_build_kms_access" {
  for_each = toset([
    google_kms_crypto_key.pinad_crypto_key.id,
    google_kms_crypto_key.oauth_tokens_key.id,
  ])
  
  crypto_key_id = each.value
  role          = "roles/cloudkms.admin"
  member        = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}

# Grant Cloud Build service account access to multi-tenant data key
resource "google_kms_crypto_key_iam_member" "cloud_build_multi_tenant_kms_access" {
  count         = var.enable_multi_tenancy ? 1 : 0
  crypto_key_id = google_kms_crypto_key.multi_tenant_data_key[0].id
  role          = "roles/cloudkms.admin"
  member        = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}
