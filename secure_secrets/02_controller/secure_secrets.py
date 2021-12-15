from kubernetes import client, config
from datetime import datetime
import os
import kopf
import subprocess
import base64


config.load_incluster_config()
k8s_api = client.CoreV1Api()

KEY_GENERATION_INTERVAL = 3600      # 1 hour for now. After testing, change it to 6 months.


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
def create_new_gpg_key(spec, body, **kwargs):
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    now_hyphen_str = now.strftime('%Y-%m-%d-%H-%M-%S')

    # keys_list = list_keys()
    # if len(keys_list) > 0:
    #     latest_key = keys_list[-1]
    #     latest_key_datetime_str = latest_key.replace('gpg-key-', '')
    #     latest_key_datetime = datetime.strptime(latest_key_datetime_str, '%Y-%m-%d-%H-%M-%S')

    #     if (now - latest_key_datetime).total_seconds() < KEY_GENERATION_INTERVAL:
    #         print(f"Last key created: {now - latest_key_datetime} ago i.e. {(now - latest_key_datetime).total_seconds()} seconds ago.")
    #         print("Valid key already present. Hence, not creating a new one!")
    #     else:
    #         subprocess.run(f"./utils/create_key.sh ", shell=True, stdout=subprocess.PIPE)
    # else:
    namespace = body.metadata.name
    result = subprocess.run(f"./utils/create_key.sh '{namespace}' '{now_str}'", shell=True, stdout=subprocess.PIPE)
    public_key = result.stdout
    public_key_b64encoded = base64.b64encode(public_key)

    secret = Secret(
        f"{namespace}-gpg-key-{now_hyphen_str}",
        namespace,
        "Opaque",
        {"key": public_key_b64encoded.decode('utf-8')}
    )

    print(f"NewKeySecret: {secret}")
    secret.create()


# @kopf.timer("secrets", interval=300, initial_delay=10, field='type', value='Opaque')      # Every 5 minutes
# def encrypt_all_secrets(spec, body, **kwargs):
#     name = body.metadata.name
#     namespace = body.metadata.namespace
#     data = body['data']

#     keys_list = list_keys()
#     for key, value in data.items():
#         encrypt(value, keys_list)


# def list_keys():
#     keys_result = subprocess.run("gpg --list-keys | grep 'gpg-key-'", shell=True, stdout=subprocess.PIPE)
#     keys_info_strings = keys_result.stdout.decode('utf-8')
#     keys_info_list = filter(None, keys_info_strings.split('\n'))
#     keys_list = list(map(lambda k: k.split()[2], keys_info_list))
#     keys_list.sort()

#     return keys_list


# def encrypt(text, keys_list):
#     input_file_name = "text_file"
#     output_file_name = "text_file_encrypted"
#     latest_key_name = keys_list[-1]

#     input_file = open(input_file_name, "w")
#     input_file.write(text)

#     if os.path.exists(output_file_name):
#         os.remove(output_file_name)

#     subprocess.run(f"gpg --output {output_file_name} --armor --encrypt --recipient {latest_key_name} {input_file_name}", shell=True, stdout=subprocess.PIPE)

#     input_file.close()
#     if os.path.exists(input_file_name):
#         os.remove(input_file_name)

#     output_file = open(output_file_name, "r")
#     print(f"Encrypted file content: {output_file.read()}")


# def decrypt(text, keys_list):
#     pass
