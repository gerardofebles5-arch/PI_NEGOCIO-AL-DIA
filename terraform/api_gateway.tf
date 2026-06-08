# API Gateway Configuration for (π)NAD V6.0 - FASE_3 Implementation
# Google Cloud API Gateway para gestión de API REST con autenticación y rate limiting

resource "google_api_gateway_api" "pinad_api" {
  provider = google-beta
  name     = "pinad-api-gateway"
  display_name = "(π)NAD API Gateway"
  
  labels = {
    app        = "pinad"
    version    = "v6.0"
    component  = "api-gateway"
    managed-by = "terraform"
  }
}

# API Config para entorno de producción
resource "google_api_gateway_api_config" "pinad_api_config_prod" {
  provider = google-beta
  api      = google_api_gateway_api.pinad_api.id
  project  = var.project_id
  display_name = "Production API Config"
  
  gateway_config {
    backend_config {
      google_service_account = google_service_account.api_gateway_sa.email
    }
  }
  
  openapi_documents {
    document {
      path     = "openapi-spec.yaml"
      contents = filebase64("${path.module}/openapi-spec.yaml")
    }
  }
  
  labels = {
    environment = "production"
  }
}

# API Config para entorno de desarrollo
resource "google_api_gateway_api_config" "pinad_api_config_dev" {
  provider = google-beta
  api      = google_api_gateway_api.pinad_api.id
  project  = var.project_id
  display_name = "Development API Config"
  
  gateway_config {
    backend_config {
      google_service_account = google_service_account.api_gateway_sa.email
    }
  }
  
  openapi_documents {
    document {
      path     = "openapi-spec-dev.yaml"
      contents = filebase64("${path.module}/openapi-spec-dev.yaml")
    }
  }
  
  labels = {
    environment = "development"
  }
}

# Gateway para producción
resource "google_api_gateway_gateway" "pinad_gateway_prod" {
  provider = google-beta
  name     = "pinad-gateway-prod"
  display_name = "(π)NAD Production Gateway"
  region   = var.region
  
  api_config = google_api_gateway_api_config.pinad_api_config_prod.id
  
  labels = {
    app        = "pinad"
    version    = "v6.0"
    component  = "api-gateway"
    environment = "production"
    managed-by = "terraform"
  }
}

# Gateway para desarrollo
resource "google_api_gateway_gateway" "pinad_gateway_dev" {
  provider = google-beta
  name     = "pinad-gateway-dev"
  display_name = "(π)NAD Development Gateway"
  region   = var.region
  
  api_config = google_api_gateway_api_config.pinad_api_config_dev.id
  
  labels = {
    app        = "pinad"
    version    = "v6.0"
    component  = "api-gateway"
    environment = "development"
    managed-by = "terraform"
  }
}

# Service Account para API Gateway
resource "google_service_account" "api_gateway_sa" {
  account_id   = "pinad-api-gateway-sa"
  display_name = "PINAD API Gateway Service Account"
  description  = "Service account for API Gateway to invoke Cloud Run"
}

# IAM bindings para API Gateway Service Account
resource "google_project_iam_member" "api_gateway_cloudrun_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.api_gateway_sa.email}"
}

resource "google_project_iam_member" "api_gateway_logging_admin" {
  project = var.project_id
  role    = "roles/logging.admin"
  member  = "serviceAccount:${google_service_account.api_gateway_sa.email}"
}

resource "google_project_iam_member" "api_gateway_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.api_gateway_sa.email}"
}

# API Key para autenticación
resource "google_api_gateway_api_key" "pinad_api_key" {
  provider = google-beta
  name     = "pinad-api-key"
  display_name = "(π)NAD API Key"
  
  labels = {
    app        = "pinad"
    version    = "v6.0"
    component  = "api-gateway"
    managed-by = "terraform"
  }
}

# API Key para desarrollo
resource "google_api_gateway_api_key" "pinad_api_key_dev" {
  provider = google-beta
  name     = "pinad-api-key-dev"
  display_name = "(π)NAD Development API Key"
  
  labels = {
    app        = "pinad"
    version    = "v6.0"
    component  = "api-gateway"
    environment = "development"
    managed-by = "terraform"
  }
}
