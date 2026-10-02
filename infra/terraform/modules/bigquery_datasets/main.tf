# One BigQuery dataset per storage layer (raw, staging, curated, marts, ops).

variable "project_id" {
  type = string
}

variable "location" {
  type        = string
  description = "BigQuery location. Keep it next to Cloud Storage to avoid egress costs."
}

variable "env" {
  type = string
}

variable "labels" {
  type = map(string)
}

variable "default_table_expiration_days" {
  type        = number
  description = "The sandbox allows at most 60 days. null means tables never expire."
  default     = 60
}

locals {
  layers = {
    raw     = "Unmodified source snapshots"
    staging = "Parsed, typed and contract-validated records"
    curated = "Cleaned, deduplicated, enriched entities"
    marts   = "Consumer-facing data products"
    ops     = "Platform metadata: data quality results, freshness, agent logs"
  }

  expiration_ms = var.default_table_expiration_days == null ? null : var.default_table_expiration_days * 24 * 60 * 60 * 1000
}

resource "google_bigquery_dataset" "layer" {
  for_each = local.layers

  project                     = var.project_id
  dataset_id                  = "${var.env}_${each.key}"
  friendly_name               = "${var.env} ${each.key}"
  description                 = each.value
  location                    = var.location
  default_table_expiration_ms = local.expiration_ms
  delete_contents_on_destroy  = var.env == "dev"

  labels = merge(var.labels, { layer = each.key })
}

output "dataset_ids" {
  description = "Map of layer name to dataset ID"
  value       = { for k, d in google_bigquery_dataset.layer : k => d.dataset_id }
}
