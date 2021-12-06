from kubernetes import client, config
from datetime import datetime
import kopf
import subprocess


config.load_incluster_config()
k8s_api = client.CoreV1Api()


class Secret:
    def __init__(self, ss_api, ss_kind, ss_uid, ss_name, ss_namespace, data_type, data, decryption_key_name):
        self.name = ss_name
        self.namespace = ss_namespace
        self.data_type = data_type
        self.data = data
        self.decryption_key_name = decryption_key_name
        self.ownerReferences = [{'apiVersion': ss_api, 'kind': ss_kind, 'uid': ss_uid, 'name': ss_name, 'namespace': ss_namespace}]

    def __str__(self):
        return (f"""
        Secret:
            name: {self.name}
            namespace: {self.namespace}
            data_type: {self.data_type}
            data: {self.data}
            decryption_key_name: {self.decryption_key_name}
            ownerReferences: {self.ownerReferences}
        """)

    def create(self):
        sec = client.V1Secret()
        sec.metadata = client.V1ObjectMeta(name = self.name, owner_references = self.ownerReferences)
        sec.type = self.data_type
        sec.data = {"username": "bXl1c2VybmFtZQ==", "password": "bXlwYXNzd29yZA=="}

        k8s_api.create_namespaced_secret(namespace=self.namespace, body=sec)


@kopf.on.create("securesecrets")
def create_secret(spec, body, **kwargs):
    secret = Secret(
        body["apiVersion"],
        body["kind"],
        body["metadata"]["uid"],
        body["metadata"]["name"],
        body["metadata"]["namespace"],
        spec["secretType"],
        spec["data"],
        spec["decryptionKeyName"]
    )

    print(secret)           # Comment this line after testing

    secret.create()

@kopf.timer("securesecrets", interval=15780000) # 6 months
def update_gpg_key(namespace, name, spec, status, **kwargs):
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    result = subprocess.run(['./utils/create_key.sh'], stdout=subprocess.PIPE)
    print(result.stdout)
