variable "project" {
  description = "Project"
  default     = "terraform-demo-448313"
}

variable "region" {
  description = "Project region"
  default     = "us-central1"
}

variable "location" {
  description = "Project location"
  default     = "EU"
}

variable "bq_dataset_name" {
  description = "BigQuery dataset name"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "Storage bucket name"
  default     = "terraform-demo-448313-terraform-bucket"
}

variable "gcs_storage_class" {
  description = "Bucket Storage class"
  default     = "STANDARD"
}