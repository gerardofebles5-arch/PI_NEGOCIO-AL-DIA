# Cloud Monitoring configuration for (π)NAD

# Create notification channels
resource "google_monitoring_notification_channel" "pinad_alerts" {
  count = length(var.notification_channels) > 0 ? 1 : 0
  
  project      = var.project_id
  display_name = var.notification_channels[0].display_name
  type         = var.notification_channels[0].type
  
  labels = {
    email_address = var.notification_channels[0].email
  }
  
  enabled = true
}

# Create uptime check for Cloud Run service
resource "google_monitoring_uptime_check_config" "pinad_uptime" {
  count = var.enable_monitoring ? 1 : 0
  
  display_name = "(π)NAD API Uptime Check"
  project      = var.project_id
  
  http_check {
    path         = "/health"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_cloud_run_v2_service.pinad_api[0].uri
    }
  }
  
  timeout         = "10s"
  period          = "60s"
  selected_regions = ["USA", "EUROPE", "ASIA_PACIFIC"]
  
  content_matchers {
    content = "OK"
  }
}

# Create alert policy for uptime check
resource "google_monitoring_alert_policy" "uptime_alert" {
  count = var.enable_monitoring ? 1 : 0
  
  display_name = "(π)NAD API Uptime Alert"
  project      = var.project_id
  
  conditions {
    display_name = "Uptime Check Failure"
    condition_threshold {
      filter     = "resource.type=\"uptime_url\" AND metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\""
      duration   = "300s"
      comparison = "COMPARISON_LT"
      threshold_value = 1
      aggregations {
        alignment_period     = "60s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields    = ["resource.label.project_id"]
      }
    }
  }
  
  alert_strategy {
    auto_close = "86400s"
  }
  
  notification_channels = var.enable_monitoring && length(var.notification_channels) > 0 ? [google_monitoring_notification_channel.pinad_alerts[0].id] : []
  
  enabled = true
}

# Create alert policy for Cloud Run error rate
resource "google_monitoring_alert_policy" "error_rate_alert" {
  count = var.enable_monitoring ? 1 : 0
  
  display_name = "(π)NAD API Error Rate Alert"
  project      = var.project_id
  
  conditions {
    display_name = "High Error Rate"
    condition_threshold {
      filter     = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 10
      aggregations {
        alignment_period     = "60s"
        per_series_aligner = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields    = ["resource.label.service_name"]
      }
    }
  }
  
  alert_strategy {
    auto_close = "86400s"
  }
  
  notification_channels = var.enable_monitoring && length(var.notification_channels) > 0 ? [google_monitoring_notification_channel.pinad_alerts[0].id] : []
  
  enabled = true
}

# Create alert policy for Cloud Run latency
resource "google_monitoring_alert_policy" "latency_alert" {
  count = var.enable_monitoring ? 1 : 0
  
  display_name = "(π)NAD API Latency Alert"
  project      = var.project_id
  
  conditions {
    display_name = "High Latency"
    condition_threshold {
      filter     = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\" AND metric.label.response_code_class=\"2xx\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 1000 # 1 second
      aggregations {
        alignment_period     = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields    = ["resource.label.service_name"]
      }
    }
  }
  
  alert_strategy {
    auto_close = "86400s"
  }
  
  notification_channels = var.enable_monitoring && length(var.notification_channels) > 0 ? [google_monitoring_notification_channel.pinad_alerts[0].id] : []
  
  enabled = true
}

# Create alert policy for Cloud Run instance count
resource "google_monitoring_alert_policy" "instance_count_alert" {
  count = var.enable_monitoring ? 1 : 0
  
  display_name = "(π)NAD API Instance Count Alert"
  project      = var.project_id
  
  conditions {
    display_name = "High Instance Count"
    condition_threshold {
      filter     = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/instance_count\""
      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = var.cloud_run_max_instances * 0.8
      aggregations {
        alignment_period     = "60s"
        per_series_aligner = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields    = ["resource.label.service_name"]
      }
    }
  }
  
  alert_strategy {
    auto_close = "86400s"
  }
  
  notification_channels = var.enable_monitoring && length(var.notification_channels) > 0 ? [google_monitoring_notification_channel.pinad_alerts[0].id] : []
  
  enabled = true
}

# Create custom dashboard for (π)NAD
resource "google_monitoring_dashboard" "pinad_dashboard" {
  count = var.enable_monitoring ? 1 : 0
  
  dashboard_json = jsonencode({
    displayName = "(π)NAD Monitoring Dashboard"
    gridLayout = {
      columns = 2
      widgets = [
        {
          title = "Request Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                unitOverride = "1"
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                  aggregation = {
                    alignmentPeriod = "60s"
                    perSeriesAligner = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Error Rate"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                unitOverride = "1"
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
                  aggregation = {
                    alignmentPeriod = "60s"
                    perSeriesAligner = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Latency (P99)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                unitOverride = "s"
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\" AND metric.label.response_code_class=\"2xx\""
                  aggregation = {
                    alignmentPeriod = "60s"
                    perSeriesAligner = "ALIGN_PERCENTILE_99"
                    crossSeriesReducer = "REDUCE_MEAN"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Instance Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                unitOverride = "1"
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/instance_count\""
                  aggregation = {
                    alignmentPeriod = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        }
      ]
    }
  })
  
  project = var.project_id
}
