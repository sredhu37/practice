terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.1.0"
    }
  }

  backend "gcs" {
    bucket = "sunny_gcp1_tf_state_dev"
    prefix = "terraform/state"
  }
}

provider "google" {
  credentials = file(var.gcp_sa_credentials_file_path)
  project     = var.gcp_project
  region      = var.gcp_region
}

resource "google_container_cluster" "primary" {
  name               = var.gke_cluster.name
  location           = var.gke_cluster.location
  initial_node_count = var.gke_cluster.initial_node_count

  cluster_autoscaling {
    enabled = true
    resource_limits {
      resource_type = "cpu"
      minimum       = var.gke_cluster.cluster_cpu_min_limit
      maximum       = var.gke_cluster.cluster_cpu_max_limit
    }
    resource_limits {
      resource_type = "memory"
      minimum       = var.gke_cluster.cluster_memory_min_limit
      maximum       = var.gke_cluster.cluster_memory_max_limit
    }
  }
}
