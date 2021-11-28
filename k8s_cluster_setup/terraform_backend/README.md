# Create a bucket in GCS

## Pre-requisites:

1. Create `GCP account`.
2. Create `project` in GCP account from Step 1.
3. Create `service account` for the project in Step 2.

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