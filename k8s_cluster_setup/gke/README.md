# Create GKE cluster using Terraform

## Pre-requisites

1. Make sure that you have Terraform backend ready. If not, please follow [this documentation](../terraform_backend/README.md).
2. Install `gcloud cli` if not already installed.
3. Put the service account `json key` in this folder. Name of the file: `secret_tf_gcp_sa_key.json`
4. `gcloud auth application-default login`

## Cluster creation

```
terraform fmt
terraform init
terraform validate
terraform plan
terraform apply -auto-approve
```

## Destroy cluster

After you are done experimenting, make sure to delete the cluster to avoid any additional cost.

```
terraform destroy -auto-approve
```
