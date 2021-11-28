gcp_sa_credentials_file_path = "secret_tf_gcp_sa_key.json"
gcp_project                  = "sunny-gcp1-practice"
gke_cluster = {
  name                     = "sunny-gcp1-gke-cluster-1"
  location                 = "asia-south1"
  initial_node_count       = 2
  cluster_cpu_min_limit    = 1
  cluster_cpu_max_limit    = 12
  cluster_memory_min_limit = 1
  cluster_memory_max_limit = 64
}
