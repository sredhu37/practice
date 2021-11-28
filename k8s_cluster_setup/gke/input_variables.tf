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

variable "gke_cluster" {
  type = object({
    name                     = string
    location                 = string
    initial_node_count       = number
    cluster_cpu_min_limit    = number
    cluster_cpu_max_limit    = number
    cluster_memory_min_limit = number
    cluster_memory_max_limit = number
  })
}