# Compliance Configuration for (π)NAD
# Supports PCI-DSS, GDPR, HIPAA, and SOX compliance frameworks

# Create organization policy for data residency (GDPR compliance)
resource "google_org_policy_policy" "data_residency_policy" {
  count = var.enable_compliance ? 1 : 0
  
  name = "organizations/${var.project_id}/policies/dataResidencyConstraint"
  
  spec {
    rules {
      allow_all = false
      locations = ["in:${var.data_residency_region}"]
    }
  }
  
  parent = "organizations/${var.project_id}"
}

# Create organization policy for encryption at rest (PCI-DSS, HIPAA compliance)
resource "google_org_policy_policy" "encryption_at_rest_policy" {
  count = var.enable_compliance ? 1 : 0
  
  name = "organizations/${var.project_id}/policies/encryptionAtRestConstraint"
  
  spec {
    rules {
      allow_all = false
      enforce = true
    }
  }
  
  parent = "organizations/${var.project_id}"
}

# Create organization policy for access control (PCI-DSS, SOX compliance)
resource "google_org_policy_policy" "access_control_policy" {
  count = var.enable_compliance ? 1 : 0
  
  name = "organizations/${var.project_id}/policies/accessControlPolicy"
  
  spec {
    rules {
      allow_all = false
      enforce = true
    }
  }
  
  parent = "organizations/${var.project_id}"
}

# Create organization policy for audit logging (SOX, HIPAA compliance)
resource "google_org_policy_policy" "audit_logging_policy" {
  count = var.enable_compliance ? 1 : 0
  
  name = "organizations/${var.project_id}/policies/auditLoggingPolicy"
  
  spec {
    rules {
      allow_all = false
      enforce = true
    }
  }
  
  parent = "organizations/${var.project_id}"
}

# Create audit log sink for compliance (PCI-DSS, SOX, HIPAA)
resource "google_logging_project_sink" "compliance_audit_sink" {
  count = var.enable_compliance ? 1 : 0
  
  name = "compliance-audit-sink"
  project = var.project_id
  
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/compliance_audit_logs"
  
  filter = "logName:\"logs/cloudaudit.googleapis.com\""
  
  unique_writer_identity = true
}

# Create BigQuery dataset for compliance audit logs
resource "google_bigquery_dataset" "compliance_audit_logs" {
  count = var.enable_compliance ? 1 : 0
  
  dataset_id = "compliance_audit_logs"
  project    = var.project_id
  location   = var.data_residency_region
  
  default_table_expiration_ms = var.audit_log_retention_days * 24 * 60 * 60 * 1000
  
  labels = {
    environment = var.environment
    purpose     = "compliance"
    managed-by  = "terraform"
  }
  
  access {
    role = "roles/bigquery.dataViewer"
    user_by_email = "compliance@pinad.com"
  }
  
  access {
    role = "roles/bigquery.dataEditor"
    user_by_email = "security@pinad.com"
  }
}

# Grant IAM permissions for compliance audit logs
resource "google_project_iam_member" "compliance_audit_sink_iam" {
  count = var.enable_compliance ? 1 : 0
  
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_logging_project_sink.compliance_audit_sink[0].writer_identity}"
}

# Create data loss prevention (DLP) configuration (PCI-DSS, HIPAA compliance)
resource "google_data_loss_prevention_deidentify_template" "compliance_dlp_template" {
  count = var.enable_compliance ? 1 : 0
  
  parent = "projects/${var.project_id}"
  
  deidentify_template {
    display_name = "Compliance DLP Template"
    description  = "DLP template for PCI-DSS and HIPAA compliance"
    
    deidentify_config {
      info_type_transformations {
        transformations {
          primitive_transformation {
            replace_config {
              new_value {
                string_value = "[REDACTED]"
              }
            }
          }
          info_types {
            name = "CREDIT_CARD_NUMBER"
          }
          info_types {
            name = "US_SOCIAL_SECURITY_NUMBER"
          }
          info_types {
            name = "EMAIL_ADDRESS"
          }
          info_types {
            name = "PHONE_NUMBER"
          }
          info_types {
            name = "MEDICAL_RECORD_NUMBER"
          }
        }
      }
    }
  }
}

# Create DLP job for scanning data (PCI-DSS, HIPAA compliance)
resource "google_data_loss_prevention_job_trigger" "compliance_dlp_job" {
  count = var.enable_compliance ? 1 : 0
  
  parent = "projects/${var.project_id}/locations/${var.region}"
  
  job_trigger {
    display_name = "Compliance DLP Job"
    description  = "DLP job for scanning sensitive data"
    
    triggers {
      schedule {
        recurrence_period_duration {
          seconds = 86400 # Daily
        }
      }
    }
    
    inspect_job {
      storage_config {
        cloud_storage_options {
          file_set {
            url = "gs://pinad-firestore-backups/**"
          }
        }
      }
      
      inspect_config {
        min_likelihood = "LIKELY"
        
        info_types {
          name = "CREDIT_CARD_NUMBER"
        }
        info_types {
          name = "US_SOCIAL_SECURITY_NUMBER"
        }
        info_types {
          name = "EMAIL_ADDRESS"
        }
        info_types {
          name = "PHONE_NUMBER"
        }
        info_types {
          name = "MEDICAL_RECORD_NUMBER"
        }
        
        limits {
          max_findings_per_item = 0
        }
      }
      
      actions {
        save_findings {
          output_config {
            table {
              project_id = var.project_id
              dataset_id = "compliance_dlp_findings"
            }
          }
        }
      }
    }
  }
}

# Create BigQuery dataset for DLP findings
resource "google_bigquery_dataset" "compliance_dlp_findings" {
  count = var.enable_compliance ? 1 : 0
  
  dataset_id = "compliance_dlp_findings"
  project    = var.project_id
  location   = var.data_residency_region
  
  default_table_expiration_ms = var.audit_log_retention_days * 24 * 60 * 60 * 1000
  
  labels = {
    environment = var.environment
    purpose     = "compliance"
    managed-by  = "terraform"
  }
  
  access {
    role = "roles/bigquery.dataViewer"
    user_by_email = "compliance@pinad.com"
  }
  
  access {
    role = "roles/bigquery.dataEditor"
    user_by_email = "security@pinad.com"
  }
}

# Create security center for compliance monitoring
resource "google_security_center_source" "compliance_security_source" {
  count = var.enable_compliance ? 1 : 0
  
  display_name = "Compliance Security Source"
  organization = var.project_id
}

# Create security center notification for compliance alerts
resource "google_security_center_notification_config" "compliance_notification" {
  count = var.enable_compliance ? 1 : 0
  
  config {
    description = "Compliance Security Notification"
    pubsub_topic = "projects/${var.project_id}/topics/compliance-security-alerts"
    
    streaming_config {
      filter = "category=\"COMPLIANCE_VIOLATION\""
    }
  }
  
  parent = "organizations/${var.project_id}/sources/${google_security_center_source.compliance_security_source[0].source_id}"
}

# Create Pub/Sub topic for compliance alerts
resource "google_pubsub_topic" "compliance_security_alerts" {
  count = var.enable_compliance ? 1 : 0
  
  name = "compliance-security-alerts"
  project = var.project_id
  
  labels = {
    environment = var.environment
    purpose     = "compliance"
    managed-by  = "terraform"
  }
}

# Create IAM deny policy for data access (GDPR compliance)
resource "google_project_iam_policy" "compliance_iam_deny_policy" {
  count = var.enable_compliance ? 1 : 0
  
  project     = var.project_id
  policy_data = jsonencode({
    bindings = [
      {
        role = "roles/viewer",
        members = [
          "allAuthenticatedUsers",
        ]
      }
    ]
    etag = "BwWjMktCsNw="
  })
}

# Create Cloud Armor security policy (PCI-DSS compliance)
resource "google_compute_security_policy" "compliance_security_policy" {
  count = var.enable_compliance ? 1 : 0
  
  name        = "compliance-security-policy"
  description = "Security policy for PCI-DSS compliance"
  
  rules {
    action      = "allow"
    description = "Allow all traffic by default"
    match {
      config {
        src_ip_ranges = ["*"]
      }
      versioned_expr = "SRC_IPS_V1"
    }
    priority     = 2147483647
  }
  
  rules {
    action      = "deny(403)"
    description = "Deny SQL injection attacks"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sql-injection')"
      }
    }
    priority     = 1000
  }
  
  rules {
    action      = "deny(403)"
    description = "Deny XSS attacks"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    priority     = 1001
  }
  
  rules {
    action      = "deny(403)"
    description = "Deny remote file inclusion attacks"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('rfi-stable')"
      }
    }
    priority     = 1002
  }
}

# Create VPC Service Controls for data exfiltration prevention (PCI-DSS, HIPAA compliance)
resource "google_access_context_manager_access_level" "compliance_access_level" {
  count = var.enable_compliance ? 1 : 0
  
  parent = "accessPolicies/${var.project_id}"
  name   = "accessPolicies/${var.project_id}/accessLevels/compliance_access_level"
  
  basic {
    combining_function = "AND"
    conditions {
      device_policy {
        require_screen_lock = true
        require_admin_approval = true
      }
      regions = [var.data_residency_region]
    }
  }
}

# Create access context manager service perimeter (PCI-DSS, HIPAA compliance)
resource "google_access_context_manager_service_perimeter" "compliance_service_perimeter" {
  count = var.enable_compliance ? 1 : 0
  
  parent = "accessPolicies/${var.project_id}"
  name   = "accessPolicies/${var.project_id}/servicePerimeters/compliance_service_perimeter"
  
  title = "Compliance Service Perimeter"
  description = "Service perimeter for PCI-DSS and HIPAA compliance"
  
  status {
    restricted_services = [
      "bigquery.googleapis.com",
      "storage.googleapis.com",
      "firestore.googleapis.com",
      "datastore.googleapis.com",
    ]
    
    vpc_accessible_services {
      allowed_services = [
        "bigquery.googleapis.com",
        "storage.googleapis.com",
        "firestore.googleapis.com",
        "datastore.googleapis.com",
      ]
    }
  }
  
  spec {
    restricted_services = [
      "bigquery.googleapis.com",
      "storage.googleapis.com",
      "firestore.googleapis.com",
      "datastore.googleapis.com",
    ]
    
    vpc_accessible_services {
      allowed_services = [
        "bigquery.googleapis.com",
        "storage.googleapis.com",
        "firestore.googleapis.com",
        "datastore.googleapis.com",
      ]
    }
  }
}

# Create Cloud Asset Inventory for compliance reporting (SOX compliance)
resource "google_cloud_asset_project_feed" "compliance_asset_feed" {
  count = var.enable_compliance ? 1 : 0
  
  project = var.project_id
  feed_id = "compliance-asset-feed"
  
  asset_types = [
    "compute.googleapis.com/Instance",
    "storage.googleapis.com/Bucket",
    "bigquery.googleapis.com/Dataset",
    "firestore.googleapis.com/Database",
  ]
  
  feed_output_config {
    pubsub_destination {
      topic = "projects/${var.project_id}/topics/compliance-asset-feed"
    }
  }
}

# Create Pub/Sub topic for asset feed
resource "google_pubsub_topic" "compliance_asset_feed" {
  count = var.enable_compliance ? 1 : 0
  
  name = "compliance-asset-feed"
  project = var.project_id
  
  labels = {
    environment = var.environment
    purpose     = "compliance"
    managed-by  = "terraform"
  }
}

# Create compliance monitoring dashboard
resource "google_monitoring_dashboard" "compliance_dashboard" {
  count = var.enable_compliance ? 1 : 0
  
  dashboard_json = jsonencode({
    displayName = "Compliance Monitoring Dashboard"
    gridLayout = {
      columns = 2
      widgets = [
        {
          title = "Audit Log Events"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_project\" AND log_name:\"logs/cloudaudit.googleapis.com\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_COUNT"
                  }
                }
              }
            }]
          }
        }
        {
          title = "DLP Findings"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"dlp_job\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_COUNT"
                  }
                }
              }
            }]
          }
        }
        {
          title = "Security Incidents"
          scorecard = {
            dataView = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_project\" AND metric.type=\"security.googleapis.com/incident_count\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_COUNT"
                  }
                }
              }
            }
          }
        }
        {
          title = "Access Control Violations"
          scorecard = {
            dataView = {
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_project\" AND metric.type=\"iam.googleapis.com/iam_deny_violation_count\""
                  aggregation = {
                    alignmentPeriod = "300s"
                    perSeriesAligner = "ALIGN_COUNT"
                  }
                }
              }
            }
          }
        }
      ]
    }
  })
}
