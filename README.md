# For Developers/Administrators

## After creating GCP K8S cluster, run the following steps to do the setup

### Create namespaces:

`kubectl apply -f manual_setup/01_namespaces.yaml`

### Install sealed-secrets from bitnami

- Download kubeseal CLI and move to path

- `kubectl apply -n sealedsecrets -f manual_setup/02_sealedsecrets-controller.yaml`

### Install the sealing secret

- Secret is stored in my system. Can't disclose it. But deploy this secret in all the clusters in kube-system namespace.

`kubectl apply -f <path_to_secret.yaml> -n kube-system`

- Certificate(present in the secret) is used to encrypt the secrets and decrypt the sealedsecrets.

- `kubeseal --fetch-cert` will get the certificate from the latest key. A new gets generated every month. However, I will be using the older one for now as it's being used in multiple clusters.

#### Encrypt secrets to sealed-secrets:

- Create the secret.yaml file.
- Encrypt this secret using kubeseal:

  `kubeseal --cert=path_to_cert_file -o yaml --scope cluster-wide <secret.yaml >sealedsecret.yaml`

### Install argocd

- Download argocd CLI and move to path.

- `kubectl apply -n argocd -f manual_setup/03_argocd-controller.yaml`

### Install app-of-apps

`kubectl apply -f manual_setup/04_argocd-app.yaml`

### Make argocd accessible:

`kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}'`

`nodePort=$(kubectl get service argocd-server -n argocd -o "jsonpath={.spec.ports[?(@.name=='http')].nodePort}")`

Now we can access argocd UI at http://127.0.0.1:${nodePort}

### Getting credentials

Username: `admin`

Password: `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d`

### Deploy ingress controller:

`kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.41.2/deploy/static/provider/cloud/deploy.yaml`


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
