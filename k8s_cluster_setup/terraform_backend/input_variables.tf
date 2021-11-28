variable "gcp_sa_credentials_file_path" {
  type = string
}

variable "gcp_project" {
  type = string
}

variable "gcp_region" {
  type    = string
  default = "asia-south1" # Mumbai, India
}

variable "tf_backend_dev_gcs_bucket_name" {
  type = string
}

variable "tf_backend_dev_gcs_bucket_location" {
  type    = string
  default = "ASIA-SOUTH1" # Mumbai, India
}
