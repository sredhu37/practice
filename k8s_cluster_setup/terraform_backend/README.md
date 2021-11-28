# Create a bucket in GCS

## Pre-requisites:

1. Create `GCP account`.
2. Create `project` in GCP account from Step 1.
3. Create `service account` for the project in Step 2.
4. Put the service account `json key` in this folder. Name of the file: `secret_tf_gcp_sa_key.json`
5. Install `Terraform CLI`.

## Create bucket

<b>NOTE:</b> Execute this locally on your dev-machine and do not push the `terraform.tfstate*` files to any VCS/SCM, but keep them safe on the dev-machine.

```
cd k8s_cluster_setup/terraform_backend
terraform fmt
terraform init
terraform validate
terraform plan
terraform apply -auto-approve
```

## Delete bucket

Once you are done with experimenting with the project, feel free to destroy the infra in order to avoid additional cost.

`terraform destroy`