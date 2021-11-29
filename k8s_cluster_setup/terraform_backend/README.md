# Create a bucket in GCS

## Pre-requisites:

Complete the pre-requisites from [main README.md](../../README.md).

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

```
terraform destroy
```