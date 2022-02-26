# 1. For users

Nothing yet!!!

# 2. For Developers/Administrators

## 2.1. Pre-requisites

Follow the steps mentioned in https://github.com/sredhu37/do-terraform-gcp/blob/main/README.md

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

### 2.4.7. Deploy ingress controller:

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

### Prod version (On GKE)

```
helm install -n jenkins jenkins jenkins/sunny-jenkins-helm/.
```

### Check if Chart installed

```
helm ls -n jenkins
```


io.jenkins.plugins.casc.ConfiguratorException: Invalid configuration: '/var/jenkins_home/casc_config/casc.yaml' isn't a valid path.
