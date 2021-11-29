# Create GKE cluster using Terraform

## Pre-requisites

1. Complete the pre-requisites from [main README.md](../../README.md).
2. Make sure that you have Terraform backend ready. If not, please follow [this documentation](../terraform_backend/README.md).

## Cluster creation

```
cd k8s_cluster_setup/gke
gcloud auth application-default login

terraform fmt
terraform init
terraform validate
terraform plan
terraform apply -auto-approve
```
Once the GKE cluster is created:
```
gcloud container clusters get-credentials sunny-gcp1-gke-cluster-1 --region asia-south1 --project sunny-gcp1-practice

kubectl config get-contexts
```
Make sure that you are seeing your cluster in the output from the last command.

## Destroy cluster

After you are done experimenting, make sure to delete the cluster to avoid any additional cost.

```
terraform destroy -auto-approve
```
