terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.1.0"
    }
  }
}

provider "google" {
  credentials = file(var.gcp_sa_credentials_file_path)

  project = var.gcp_project
  region  = var.gcp_region
}

resource "google_storage_bucket" "tf_backend_dev" {
  name          = var.tf_backend_dev_gcs_bucket_name
  location      = var.tf_backend_dev_gcs_bucket_location
  force_destroy = true
}
