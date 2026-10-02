output "datasets" {
  description = "BigQuery datasets per layer"
  value       = module.bigquery.dataset_ids
}

output "service_accounts" {
  description = "Service account emails per component"
  value       = module.service_accounts.emails
}
