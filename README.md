# 1. For users

Nothing yet!!!

# 2. For Developers/Administrators

## 2.1. Pre-requisites

### 2.1.1. Infra Setup

Follow the steps mentioned in https://github.com/sredhu37/do-terraform-gcp/blob/main/README.md

### 2.1.2. Setup connection to GKE cluster

- ssh into `bastion` machine created in the previous step.
- `gcloud init` and follow the instructions.
- `gcloud auth init` and follow the instructions.
- Install kubectl: `sudo apt-get install kubectl`
- Install gke-gcloud-auth-plugin: `sudo apt-get install google-cloud-sdk-gke-gcloud-auth-plugin`
- Connect to GKE cluster: `gcloud container clusters get-credentials gke-private-cluster-europe-west4 --zone europe-west4-a --project sunny-tf-gcp-5`


## 2.2. Setup

### 2.2.1. Create namespaces:

```
kubectl apply -f https://raw.githubusercontent.com/sredhu37/practice/master/manual_setup/01_namespaces.yaml
```

### 2.2.2. Install SealedSecrets

```
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.17.3/controller.yaml
```

Download and install `kubeseal` [from here](https://github.com/bitnami-labs/sealed-secrets/releases/tag/v0.17.3).

### 2.2.3. Install argocd

```
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

### 2.2.4. Install app-of-apps

```
kubectl apply -f https://raw.githubusercontent.com/sredhu37/practice/master/manual_setup/02_argocd-app.yaml
```

### 2.2.5. Access argocd:

```
kubectl get svc -n argocd argocd-server -o "jsonpath={.status.loadBalancer.ingress[*].ip}"
```

Now access argocd UI using the value from previous command.

### 2.2.6. Getting credentials

Username: `admin`

Password: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`


It will take some time for app-of-apps to create other errors. There might be some error displayed. Just wait for 5-10 minutes, it will work automatically.

### 2.2.7. Setup Ingress

- Create Cloud DNS zone and get nameservers from it.
- Add/Update the custom name servers in Google Domains.
- Ingress object creates the external HTTP(S) LB in GCP. Check the ingress object in argocd ui and get the IP address.
- Add a record set in the DNS zone with proper prefix and proper IP address.
- Wait for 10 minutes and try the url in the browser: `http://argocd.sunnyredhu.com`. Don't forget the http.
- Repeat the above steps for resume too: `http://sunnyredhu.com`. Don't forget the http.

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
