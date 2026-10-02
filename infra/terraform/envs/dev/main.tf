terraform {
  required_version = ">= 1.6"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0, < 8.0"
    }
  }

  # Local state for now: a Cloud Storage bucket for remote state needs a billing account (ADR-007).
  # backend "gcs" {
  #   bucket = "<project-id>-tfstate"
  #   prefix = "envs/dev"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  env = "dev"

  labels = {
    project    = "city-pulse-nyc"
    env        = local.env
    managed_by = "terraform"
  }
}

resource "google_project_service" "api" {
  for_each = toset([
    "bigquery.googleapis.com",
    "iam.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

module "bigquery" {
  source = "../../modules/bigquery_datasets"

  project_id                    = var.project_id
  location                      = var.region
  env                           = local.env
  labels                        = local.labels
  default_table_expiration_days = 60

  depends_on = [google_project_service.api]
}

module "service_accounts" {
  source = "../../modules/service_accounts"

  project_id  = var.project_id
  env         = local.env
  dataset_ids = module.bigquery.dataset_ids

  depends_on = [google_project_service.api]
}
