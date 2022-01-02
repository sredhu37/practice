from kubernetes import client, config
from datetime import datetime
import os
import kopf
import subprocess
import base64
from cryptography.fernet import Fernet

config.load_incluster_config()
k8s_api = client.CoreV1Api()

KEY_GENERATION_INTERVAL = 3600      # 1 hour for now. After testing, change it to 6 months.
KEY_TYPE = 'fernet-key'

class Secret:
    def __init__(self, name, namespace, data_type, data, ss=None):
        self.name = name
        self.namespace = namespace
        self.data_type = data_type
        self.data = data
        self.decryption_key_name = None
        self.owner_references = None

        if ss is not None:
            self.decryption_key_name = ss['decryption_key_name']
            self.owner_references = [{
                'apiVersion': ss['api'],
                'kind': ss['kind'],
                'uid': ss['uid'],
                'name': name,
                'namespace': namespace
            }]

    def __str__(self):
        return (f"""
        Secret:
            name: {self.name}
            namespace: {self.namespace}
            data_type: {self.data_type}
            data: {self.data}
            decryption_key_name: {self.decryption_key_name}
            owner_references: {self.owner_references}
        """)

    def create(self):
        sec = client.V1Secret()

        sec.metadata = client.V1ObjectMeta(name = self.name, owner_references = self.owner_references)
        sec.type = self.data_type
        sec.data = self.data

        k8s_api.create_namespaced_secret(namespace=self.namespace, body=sec)


# @kopf.on.create("securesecrets")
# def create_secret(spec, body, **kwargs):
#     secret = Secret(
#         body["metadata"]["name"],
#         body["metadata"]["namespace"],
#         spec["secretType"],
#         spec["data"],
#         {
#             'api': body["apiVersion"],
#             'kind': body["kind"],
#             'uid': body["metadata"]["uid"],
#             'decryption_key_name': spec["decryptionKeyName"]
#         }
#     )

#     print(secret)           # Comment this line after testing

#     secret.create()


@kopf.timer("namespaces", interval=KEY_GENERATION_INTERVAL)
def create_new_key(spec, body, **kwargs):
    now = datetime.now()
    namespace = body.metadata.name

    # Ignore kube namespaces
    if namespace.startswith('kube-'):
        print(f"Skipping namespace: {namespace} as it starts with kube!")
    else:
        keys_list = list_keys(namespace)
        # print(f"keys_list for namespace {namespace}: {keys_list}")
        if len(keys_list) > 0:
            latest_key = keys_list[-1]
            latest_key_name = latest_key.metadata.name
            latest_key_datetime_str = latest_key_name.replace(f"{namespace}-fernet-key-", '')
            latest_key_datetime = datetime.strptime(latest_key_datetime_str, '%Y-%m-%d-%H-%M-%S')

            if (now - latest_key_datetime).total_seconds() < KEY_GENERATION_INTERVAL:
                print(f"Last key {latest_key_name} created: {now - latest_key_datetime} ago i.e. {(now - latest_key_datetime).total_seconds()} seconds ago. Valid key already present. Hence, not creating a new one!")
            else:
                print("All fernet keys are too old. Creating a new one.")
                create_key_and_secret(now, namespace)
        else:
            print(f"No fernet key exists for namespace: {namespace}. Creating a new one.")
            create_key_and_secret(now, namespace)


# @kopf.timer("secrets", interval=300, initial_delay=10, field='type', value='Opaque')      # Every 5 minutes
# def encrypt_all_secrets(spec, body, **kwargs):
#     name = body.metadata.name
#     namespace = body.metadata.namespace
#     data = body['data']

#     keys_list = list_keys()
#     for key, value in data.items():
#         encrypt(value, keys_list)


def list_keys(namespace):
    keys_result = k8s_api.list_namespaced_secret(namespace).items
    encryption_keys = list(filter(lambda k: k.metadata.name.startswith(f"{namespace}-{KEY_TYPE}-"), keys_result))
    sorted_keys = sorted(encryption_keys, key=lambda x: x.metadata.name)
    # print(f"Sorted keys: {sorted_keys}")
    return sorted_keys


def encrypt(text, keys_list):
    latest_key_name = keys_list[-1]

# def decrypt(text, keys_list):
#     pass

def create_key_and_secret(now, namespace):
    now_hyphen_str = now.strftime('%Y-%m-%d-%H-%M-%S')

    # Create fernet key
    fernet_key = Fernet.generate_key()
    fernet_key_b64encoded = base64.b64encode(fernet_key)

    secret = Secret(
        f"{namespace}-{KEY_TYPE}-{now_hyphen_str}",
        namespace,
        "Opaque",
        {
            "fernet_key": fernet_key_b64encoded.decode()
        }
    )

    # print(f"NewKeySecret: {secret}")
    secret.create()
    print(f"Created new fernet key: {secret.name}")
