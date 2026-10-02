# One service account per platform component, with least-privilege access per dataset.

variable "project_id" {
  type = string
}

variable "env" {
  type = string
}

variable "dataset_ids" {
  type        = map(string)
  description = "Map of layer name to dataset ID, from the bigquery_datasets module"
}

locals {
  accounts = {
    ingestion = "Pollers: write raw snapshots"
    pipelines = "Beam and Spark jobs: read raw, write staging and curated"
    transform = "dbt: read curated, write marts"
    agent     = "AI agent: read-only access to marts and ops"
  }

  grants = [
    { sa = "ingestion", layer = "raw", role = "roles/bigquery.dataEditor" },
    { sa = "pipelines", layer = "raw", role = "roles/bigquery.dataViewer" },
    { sa = "pipelines", layer = "staging", role = "roles/bigquery.dataEditor" },
    { sa = "pipelines", layer = "curated", role = "roles/bigquery.dataEditor" },
    { sa = "pipelines", layer = "ops", role = "roles/bigquery.dataEditor" },
    { sa = "transform", layer = "curated", role = "roles/bigquery.dataViewer" },
    { sa = "transform", layer = "marts", role = "roles/bigquery.dataEditor" },
    { sa = "transform", layer = "ops", role = "roles/bigquery.dataEditor" },
    { sa = "agent", layer = "marts", role = "roles/bigquery.dataViewer" },
    { sa = "agent", layer = "ops", role = "roles/bigquery.dataViewer" },
  ]
}

resource "google_service_account" "sa" {
  for_each = local.accounts

  project      = var.project_id
  account_id   = "cp-${var.env}-${each.key}"
  display_name = "City Pulse ${var.env} ${each.key}"
  description  = each.value
}

resource "google_bigquery_dataset_iam_member" "grant" {
  for_each = { for g in local.grants : "${g.sa}-${g.layer}" => g }

  project    = var.project_id
  dataset_id = var.dataset_ids[each.value.layer]
  role       = each.value.role
  member     = "serviceAccount:${google_service_account.sa[each.value.sa].email}"
}

# Running any query requires jobUser at project level; it cannot be scoped to a dataset.
resource "google_project_iam_member" "job_user" {
  for_each = local.accounts

  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.sa[each.key].email}"
}

output "emails" {
  description = "Map of component name to service account email"
  value       = { for k, sa in google_service_account.sa : k => sa.email }
}
