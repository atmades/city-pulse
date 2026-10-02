variable "project_id" {
  type        = string
  description = "Google Cloud project ID for the dev environment"
}

variable "region" {
  type        = string
  description = "us-east1: eligible for Always Free Cloud Storage and VM quotas, and closest to New York"
  default     = "us-east1"
}
