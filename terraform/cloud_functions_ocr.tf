# Cloud Functions para OCR Ultra Avanzado V5.0
# Despliegue de funciones en Python para procesamiento de documentos con Google Document AI

# Variable para la región de la Cloud Function
variable "ocr_function_region" {
  description = "Región para desplegar la Cloud Function de OCR"
  type        = string
  default     = "us-central1"
}

# Variable para el runtime de Python
variable "ocr_function_runtime" {
  description = "Runtime de Python para la Cloud Function"
  type        = string
  default     = "python310"
}

# Variable para la memoria de la Cloud Function
variable "ocr_function_memory" {
  description = "Memoria en MB para la Cloud Function de OCR"
  type        = number
  default     = 512
}

# Variable para el timeout de la Cloud Function
variable "ocr_function_timeout" {
  description = "Timeout en segundos para la Cloud Function de OCR"
  type        = number
  default     = 60
}

# Variable para el máximo de instancias
variable "ocr_function_max_instances" {
  description = "Máximo de instancias para la Cloud Function de OCR"
  type        = number
  default     = 10
}

# Bucket de origen para el código de la Cloud Function
resource "google_storage_bucket" "ocr_function_source" {
  name          = "${var.project_id}-ocr-function-source"
  location      = var.region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }
  
  labels = {
    environment = var.environment
    component  = "ocr_function"
    managed_by = "terraform"
  }
}

# Archivo de código fuente de la Cloud Function
resource "google_storage_bucket_object" "ocr_function_code" {
  name   = "ocr_ultra.zip"
  bucket = google_storage_bucket.ocr_function_source.name
  source = "${path.module}/../cloud_functions/python_functions/ocr_ultra.zip"
  
  # Nota: El archivo zip debe crearse antes de aplicar Terraform
  # Command: cd cloud_functions/python_functions && zip -r ocr_ultra.zip .
}

# Cloud Function para procesar documentos con OCR ultra avanzado
resource "google_cloudfunctions2_function" "process_document_ultra" {
  name        = "process-document-ultra"
  location    = var.ocr_function_region
  description = "Procesa documentos con OCR ultra avanzado V5.0 usando Google Document AI"
  
  build_config {
    runtime = var.ocr_function_runtime
    entry_point = "process_document_ultra"
    
    source {
      storage_source {
        bucket = google_storage_bucket.ocr_function_source.name
        object = google_storage_bucket.ocr_function_code.name
      }
    }
    
    environment_variables = {
      PROJECT_ID = var.project_id
      REGION     = var.ocr_function_region
    }
  }
  
  service_config {
    max_instance_count = var.ocr_function_max_instances
    available_memory   = var.ocr_function_memory
    timeout_seconds    = var.ocr_function_timeout
    
    environment_variables = {
      DOCUMENT_AI_PROCESSOR_ID = var.document_ai_processor_id
      SENIAT_API_KEY          = google_secret_manager_secret_version.seniat_api_key.secret_id
    }
    
    secret_environment_variables {
      secret = google_secret_manager_secret.seniat_api_key.secret_id
      key    = "SENIAT_API_KEY"
    }
  }
  
  labels = {
    environment = var.environment
    component  = "ocr_function"
    managed_by = "terraform"
  }
}

# Cloud Function para extraer datos usando plantillas
resource "google_cloudfunctions2_function" "extract_with_template" {
  name        = "extract-with-template"
  location    = var.ocr_function_region
  description = "Extrae datos de documentos usando plantillas específicas"
  
  build_config {
    runtime = var.ocr_function_runtime
    entry_point = "extract_with_template"
    
    source {
      storage_source {
        bucket = google_storage_bucket.ocr_function_source.name
        object = google_storage_bucket.ocr_function_code.name
      }
    }
    
    environment_variables = {
      PROJECT_ID = var.project_id
      REGION     = var.ocr_function_region
    }
  }
  
  service_config {
    max_instance_count = var.ocr_function_max_instances
    available_memory   = var.ocr_function_memory
    timeout_seconds    = var.ocr_function_timeout
    
    environment_variables = {
      DOCUMENT_AI_PROCESSOR_ID = var.document_ai_processor_id
    }
  }
  
  labels = {
    environment = var.environment
    component  = "ocr_function"
    managed_by = "terraform"
  }
}

# Cloud Function para obtener resumen del motor OCR
resource "google_cloudfunctions2_function" "get_ocr_summary" {
  name        = "get-ocr-summary"
  location    = var.ocr_function_region
  description = "Obtiene resumen del motor OCR y sus capacidades"
  
  build_config {
    runtime = var.ocr_function_runtime
    entry_point = "get_ocr_summary"
    
    source {
      storage_source {
        bucket = google_storage_bucket.ocr_function_source.name
        object = google_storage_bucket.ocr_function_code.name
      }
    }
    
    environment_variables = {
      PROJECT_ID = var.project_id
      REGION     = var.ocr_function_region
    }
  }
  
  service_config {
    max_instance_count = 5
    available_memory   = 256
    timeout_seconds    = 30
  }
  
  labels = {
    environment = var.environment
    component  = "ocr_function"
    managed_by = "terraform"
  }
}

# IAM: Permitir invocación pública de las Cloud Functions
resource "google_cloudfunctions2_function_iam_member" "process_document_ultra_invoker" {
  project        = google_cloudfunctions2_function.process_document_ultra.project
  location       = google_cloudfunctions2_function.process_document_ultra.location
  cloud_function = google_cloudfunctions2_function.process_document_ultra.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

resource "google_cloudfunctions2_function_iam_member" "extract_with_template_invoker" {
  project        = google_cloudfunctions2_function.extract_with_template.project
  location       = google_cloudfunctions2_function.extract_with_template.location
  cloud_function = google_cloudfunctions2_function.extract_with_template.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

resource "google_cloudfunctions2_function_iam_member" "get_ocr_summary_invoker" {
  project        = google_cloudfunctions2_function.get_ocr_summary.project
  location       = google_cloudfunctions2_function.get_ocr_summary.location
  cloud_function = google_cloudfunctions2_function.get_ocr_summary.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

# Outputs
output "process_document_ultra_function_url" {
  description = "URL de la Cloud Function para procesar documentos"
  value       = google_cloudfunctions2_function.process_document_ultra.service_config[0].uri
}

output "extract_with_template_function_url" {
  description = "URL de la Cloud Function para extraer con plantillas"
  value       = google_cloudfunctions2_function.extract_with_template.service_config[0].uri
}

output "get_ocr_summary_function_url" {
  description = "URL de la Cloud Function para obtener resumen de OCR"
  value       = google_cloudfunctions2_function.get_ocr_summary.service_config[0].uri
}

output "ocr_function_source_bucket" {
  description = "Bucket de origen para el código de la Cloud Function"
  value       = google_storage_bucket.ocr_function_source.name
}
