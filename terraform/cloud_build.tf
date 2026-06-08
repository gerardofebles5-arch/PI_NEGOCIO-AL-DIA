# Cloud Build configuration for (π)NAD CI/CD

# Create Cloud Build triggers
resource "google_cloudbuild_trigger" "pinad_triggers" {
  name        = "pinad-${var.environment}-build"
  description = "Build trigger for (π)NAD ${var.environment} environment"
  project     = var.project_id
  
  github {
    owner = "YOUR_GITHUB_OWNER"
    name  = "YOUR_GITHUB_REPO"
    push {
      branch = var.environment == "production" ? "main" : var.environment
    }
  }
  
  filename = "cloudbuild.yaml"
  
  substitutions = {
    _PROJECT_ID      = var.project_id
    _REGION          = var.region
    _ENVIRONMENT     = var.environment
    _SERVICE_NAME    = var.cloud_run_service_name
    _REVISION        = "$REVISION_ID"
    _SHORT_SHA       = "$SHORT_SHA"
  }
  
  service_account = google_service_account.cloud_build_sa.id
}

# Create Cloud Build configuration file
resource "google_storage_bucket_object" "cloudbuild_config" {
  name   = "cloudbuild.yaml"
  bucket = google_storage_bucket.terraform_state.name
  source = "${path.module}/cloudbuild.yaml"
}

# Create Cloud Build configuration for Terraform
resource "google_storage_bucket_object" "terraform_cloudbuild_config" {
  name   = "terraform-cloudbuild.yaml"
  bucket = google_storage_bucket.terraform_state.name
  source = "${path.module}/terraform-cloudbuild.yaml"
}

# Create Cloud Build trigger for Terraform
resource "google_cloudbuild_trigger" "terraform_trigger" {
  name        = "terraform-${var.environment}-build"
  description = "Terraform build trigger for (π)NAD ${var.environment} environment"
  project     = var.project_id
  
  github {
    owner = "YOUR_GITHUB_OWNER"
    name  = "YOUR_GITHUB_REPO"
    push {
      branch = var.environment == "production" ? "main" : var.environment
    }
  }
  
  filename = "terraform-cloudbuild.yaml"
  
  substitutions = {
    _PROJECT_ID      = var.project_id
    _REGION          = var.region
    _ENVIRONMENT     = var.environment
    _TERRAFORM_DIR   = "terraform"
  }
  
  service_account = google_service_account.cloud_build_sa.id
}

# Create Cloud Build trigger for feature branches
resource "google_cloudbuild_trigger" "feature_branch_trigger" {
  name        = "pinad-feature-branch-build"
  description = "Build trigger for (π)NAD feature branches"
  project     = var.project_id
  
  github {
    owner = "YOUR_GITHUB_OWNER"
    name  = "YOUR_GITHUB_REPO"
    push {
      branch = "feature/*"
    }
  }
  
  filename = "cloudbuild.yaml"
  
  substitutions = {
    _PROJECT_ID      = var.project_id
    _REGION          = var.region
    _ENVIRONMENT     = "dev"
    _SERVICE_NAME    = var.cloud_run_service_name
    _REVISION        = "$REVISION_ID"
    _SHORT_SHA       = "$SHORT_SHA"
    _NO_DEPLOY       = "true"
  }
  
  service_account = google_service_account.cloud_build_sa.id
}
