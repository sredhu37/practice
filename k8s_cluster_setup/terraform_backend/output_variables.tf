output "tf_backend_dev_gcs_bucket_info" {
  value = {
    name      = google_storage_bucket.tf_backend_dev.name
    url       = google_storage_bucket.tf_backend_dev.url
    self_link = google_storage_bucket.tf_backend_dev.self_link
  }
}
