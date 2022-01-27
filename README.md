# 1. For users

Nothing yet!!!

# 2. For Developers/Administrators

## 2.1. Pre-requisites

### Production env

* 2.1.1. [Create GCP account](https://console.cloud.google.com). (You will get 300 USD or ~ 22000 INR initially as free tier for the first 3 months.)
* 2.1.2. [Install gcloud CLI](https://cloud.google.com/sdk/docs/install) on dev-machine.
* 2.1.3. Create `project` in GCP account.
* 2.1.4. Create `service account` in the same project.
* 2.1.5. Configure gcloud using `gcloud init`.
* 2.1.6. Create `service account` in GCP and get the associated `key`.
* 2.1.7. Put the service account `json key` in `k8s_cluster_setup/terraform_backend` and `k8s_cluster_setup/gke` folders. Name the file as `secret_tf_gcp_sa_key.json`.
* 2.1.8. [Install Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli) on dev-machine.
* 2.1.9. [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) on dev-machine.
* 2.1.10. Download `argocd CLI` and move to path.


## 2.2. Create Terraform Backend

<b>NOTE:</b> Execute this locally on your dev-machine and do not push the `terraform.tfstate*` files to any VCS/SCM, but keep them safe on the dev-machine.

```
terraform -chdir="k8s_cluster_setup/terraform_backend" fmt
terraform -chdir="k8s_cluster_setup/terraform_backend" init
terraform -chdir="k8s_cluster_setup/terraform_backend" validate
terraform -chdir="k8s_cluster_setup/terraform_backend" plan
terraform -chdir="k8s_cluster_setup/terraform_backend" apply -auto-approve
```

## 2.3. Create GKE cluster

```
gcloud auth application-default login

terraform -chdir="k8s_cluster_setup/gke" fmt
terraform -chdir="k8s_cluster_setup/gke" init
terraform -chdir="k8s_cluster_setup/gke" validate
terraform -chdir="k8s_cluster_setup/gke" plan
terraform -chdir="k8s_cluster_setup/gke" apply -auto-approve
```
Once the GKE cluster is created:
```
gcloud container clusters get-credentials sunny-gcp1-gke-cluster-1 --region asia-south1-a --project sunny-gcp1-practice

kubectl config get-contexts
```
Make sure that you are seeing your cluster in the output from the last command.

## 2.4. Setup

### 2.4.1. Create namespaces:

```
kubectl apply -f https://raw.githubusercontent.com/sredhu37/practice/master/manual_setup/01_namespaces.yaml
```

### 2.4.2. Create Secure Secret K8S operator

```
kubectl apply -f https://raw.githubusercontent.com/sredhu37/secure-secrets/master/operator/secure_secret_k8s_operator.yaml
```

### 2.4.2. Install argocd

```
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

### 2.4.3. Install app-of-apps

```
kubectl apply -f https://raw.githubusercontent.com/sredhu37/practice/master/manual_setup/02_argocd-app.yaml
```

### 2.4.4. Access argocd:

```
kubectl get svc -n argocd argocd-server -o "jsonpath={.status.loadBalancer.ingress[*].ip}"
```

Now access argocd UI using the value from previous command.

### 2.4.5. Getting credentials

Username: `admin`

Password: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`

### 2.4.6. Deploy ingress controller:

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.41.2/deploy/static/provider/cloud/deploy.yaml
```

### 2.4.7. Destroy infrastructure

Once you are done with experimenting with the project, feel free to destroy the infra in order to avoid additional cost.

```
terraform -chdir="k8s_cluster_setup/gke" destroy -auto-approve

terraform -chdir="k8s_cluster_setup/terraform_backend" destroy -auto-approve
```

## TESTING JENKINS IMAGE

### Build and run docker image

```
cd jenkins/Docker

docker build -t test-jenkins-image .

docker run --name test-jenkins -d --rm \
-e admin_username=<USERNAME> \
-e admin_password=<PASSWORD> \
-p 8080:8080 -p 50000:50000 \
-v $(pwd)/jenkins_home:/var/jenkins_home \
test-jenkins-image
```

### Get list of plugins installed

Go to `<jenkins_url>/script` and run the following code:

```
Jenkins.instance.pluginManager.plugins.each{
  plugin ->
    println ("${plugin.getShortName()}:${plugin.getVersion()}")
}
```


## Install Helm chart (From Local machine)

### Prod version (On GKE)

```
helm install -n jenkins jenkins jenkins/sunny-jenkins-helm/.
```

### Check if Chart installed

```
helm ls -n jenkins
```


io.jenkins.plugins.casc.ConfiguratorException: Invalid configuration: '/var/jenkins_home/casc_config/casc.yaml' isn't a valid path.
