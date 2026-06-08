# Cloud Run configuration for (π)NAD API

# Create Cloud Run service
resource "google_cloud_run_v2_service" "pinad_api" {
  count    = var.enable_cloud_run_autoscaling ? 1 : 0
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
    
    max_instance_request_concurrency = var.cloud_run_concurrency
  }
  
  ingress = "INGRESS_TRAFFIC_ALL"
  
  # Require authentication
  traffic {
    percent = 100
    latest_revision = true
  }
}

# IAM policy for Cloud Run service
resource "google_cloud_run_v2_service_iam_policy" "pinad_api_policy" {
  count    = var.enable_cloud_run_autoscaling ? 1 : 0
  location = google_cloud_run_v2_service.pinad_api[0].location
  name     = google_cloud_run_v2_service.pinad_api[0].name
  project  = google_cloud_run_v2_service.pinad_api[0].project
  
  policy_data = jsonencode({
    bindings = [
      {
        role = "roles/run.invoker"
        members = [
          "allUsers",
        ]
      }
    ]
  })
}

# Create Cloud Run revision with autoscaling metrics
resource "google_cloud_run_v2_service" "pinad_api_autoscaling" {
  count    = var.enable_cloud_run_autoscaling ? 1 : 0
  name     = "${var.cloud_run_service_name}-autoscaled"
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
    
    max_instance_request_concurrency = var.cloud_run_concurrency
  }
  
  ingress = "INGRESS_TRAFFIC_ALL"
  
  traffic {
    percent = 100
    latest_revision = true
  }
}
