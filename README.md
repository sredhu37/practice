# 1. For users

Nothing yet!!!

# 2. For Developers/Administrators

## 2.1. Pre-requisites

* 2.1.1. Create `GCP account`. (We will get 300 USD or ~ 22000 INR initially as free tier for the first 3 months.)
* 2.1.2. Install `gcloud CLI` on dev-machine.
* 2.1.3. Create `project` in GCP account.
* 2.1.4. Create `service account` in the same project.
* 2.1.5. Configure gcloud using `gcloud init`.
* 2.1.6. Create `service account` in GCP and get the associated `key`.
* 2.1.7. Put the service account `json key` in `k8s_cluster_setup/terraform_backend` and `k8s_cluster_setup/gke` folders. Name the file as `secret_tf_gcp_sa_key.json`.
* 2.1.8. Install `Terraform CLI` on dev-machine.
* 2.1.9. Install `kubectl` on dev-machine.
* 2.1.10. Download `argocd CLI` and move to path.


## 2.2. Create Terraform Backend

Follow the steps mentioned inside [k8s_cluster_setup/terraform_backend](./k8s_cluster_setup/terraform_backend/README.md)

## 2.3. Create GKE cluster

Follow the steps mentioned inside [k8s_cluster_setup/gke](./k8s_cluster_setup/gke/README.md)

## 2.4. Setup

### 2.4.1. Create namespaces:

```
kubectl apply -f manual_setup/01_namespaces.yaml
```

### 2.4.2. Install argocd

```
kubectl apply -n argocd -f manual_setup/02_argocd-controller.yaml
```

### 2.4.3. Install app-of-apps

To get GKE server value, run the following command:
```
kubectl config view -o "jsonpath={.clusters[?(@.name == 'gke_sunny-gcp1-practice_asia-south1_sunny-gcp1-gke-cluster-1')].cluster.server}"
```

Set `.spec.destination.server` value in `manual_setup/03_argocd-app.yaml` file and all the `kind: Application` files in `argo_apps/` to the GKE server value.

Then run:
```
kubectl apply -f manual_setup/03_argocd-app.yaml
```

### 2.4.4. Access argocd:

```
kubectl get svc -n argocd argocd-server -o "jsonpath={.status.loadBalancer.ingress[*].ip}"
```

Now access argocd UI using the value from previous command.

### Getting credentials

Username: `admin`

Password: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`

### Deploy ingress controller:

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.41.2/deploy/static/provider/cloud/deploy.yaml
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

### Dev version (On Docker Desktop K8S)

`helm install -f jenkins/sunny-jenkins-helm/values-dev.yaml -n jenkins jenkins jenkins/sunny-jenkins-helm/.`

### Prod version (On GKE)

`helm install -n jenkins jenkins jenkins/sunny-jenkins-helm/.`

### Check if Chart installed

`helm ls -n jenkins`
