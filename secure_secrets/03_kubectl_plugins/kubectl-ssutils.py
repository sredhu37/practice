#############################################
# Variables naming convention               #
# o     => object                           #
# s     => string                           #
# by    => bytes                            #
# l     => list                             #
# d     => dictionary                       #
#############################################

from cryptography.fernet import Fernet
from kubernetes import client, config
import getopt, sys, base64, os, subprocess
import yaml


def print_help():
    s_help = """
        Usage:
            kubectl-ssutils.py -n <namespace> -m <method> -e <encryptionsecret> [options]

            -h, --help                  Print help
            -n, --namespace             (required) namespace where the encryption key exists
            -m, --method                (required) method to call; Valid values: encrypt, decrypt
            -e, --encryptionsecret      (required) name of the encryption secret; or an identifiable substring. Example: fernet-key
            -t, --text                  (optional) text to encrypt; Don't use it with -s, --secret
            -s, --secret                (optional) secret to encrypt; or an identifiable substring; Don't use it with -t, --text
    """

    print(s_help)
    exit()

def read_arguments():
    # Remove 1st argument from the list of command line arguments
    l_argumentList = sys.argv[1:]

    # Options
    s_options = "hn:m:e:t:s:"

    # Long options
    l_long_options = ["help", "namespace", "method", "encryptionsecret", "text", "secret"]

    try:
        # Parsing argument
        l_arguments, l_values = getopt.getopt(l_argumentList, s_options, l_long_options)
        d_arguments_result = {}

        # checking each argument
        for s_currentArgument, s_currentValue in l_arguments:
            if s_currentArgument in ("-h", "--help"):
                print_help()
            elif s_currentArgument in ("-n", "--namespace"):
                d_arguments_result["namespace"] = s_currentValue
            elif s_currentArgument in ("-m", "--method"):
                if not s_currentValue in ["encrypt", "decrypt"]:
                    print("Error: Invalid values for <method>!")
                    print_help()
                d_arguments_result["method"] = s_currentValue
            elif s_currentArgument in ("-e", "--encryptionsecret"):
                d_arguments_result["encryptionsecret"] = s_currentValue
            elif s_currentArgument in ("-t", "--text"):
                d_arguments_result["text"] = s_currentValue
            elif s_currentArgument in ("-s", "secret"):
                d_arguments_result["secret"] = s_currentValue

        # Check required arguments
        if "namespace" in d_arguments_result and "method" in d_arguments_result and "encryptionsecret" in d_arguments_result:
            return d_arguments_result
        else:
            print("Error: Missing required argument. Required arguments: namespace, method, encryptionsecret")
            print_help()

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        print_help()

def init_k8s_client():
    global O_K8S_API
    print("Loading kube config...")
    config.load_kube_config()
    O_K8S_API = client.CoreV1Api()
    print("kube config loaded successfully!")

def get_latest_cryption_secret(s_namespace, s_secret):
    global L_SECRETS_IN_NAMESPACE
    L_SECRETS_IN_NAMESPACE = O_K8S_API.list_namespaced_secret(s_namespace).items
    l_secrets_with_substring = list(filter(lambda x: s_secret in x.metadata.name, L_SECRETS_IN_NAMESPACE))
    l_secrets_with_substring.sort(key = lambda x: x.metadata.creation_timestamp, reverse=True)

    if len(l_secrets_with_substring) == 0:
        exit(f"Error: Unable to find a secret whose metadata.name has: {s_secret}")

    o_latest_cryption_secret = l_secrets_with_substring[0]

    o_fernet_key = Fernet(base64.b64decode((o_latest_cryption_secret.data)["fernet_key"]))

    return (o_latest_cryption_secret, o_fernet_key)

def encrypt_text(o_fernet_key, s_text):
    by_encrypted_text = o_fernet_key.encrypt(s_text.encode())
    return by_encrypted_text.decode()

def decrypt_text(o_fernet_key, s_text):
    by_decrypted_text = o_fernet_key.decrypt(s_text.encode())
    return by_decrypted_text.decode()

def cleanup_file(s_filepath):
    if os.path.exists(s_filepath):
        os.remove(s_filepath)

def encrypt_secrets(o_cryption_secret, o_fernet_key, l_secrets_to_encrypt):
    # print(f"Secrets to encrypt: {l_secrets_to_encrypt}")
    o_secure_secret = []
    for secret in l_secrets_to_encrypt:
        with open('securesecret-template.yaml', 'r') as ss_tempate_stream:
            try:
                o_secure_secret.append(yaml.safe_load(ss_tempate_stream))
            except yaml.YAMLError as exc:
                exit("Something wrong with reading securesecret-template.yaml. Please mail the administrator on redhu.sunny1994@gmail.com immediately: {exc}")

        o_secure_secret[-1]['metadata']['name'] = secret.metadata.name
        o_secure_secret[-1]['metadata']['namespace'] = secret.metadata.namespace
        o_secure_secret[-1]['spec']['secretType'] = secret.type
        o_secure_secret[-1]['spec']['decryptionKeyName'] = o_cryption_secret.metadata.name

        for key, value in secret.data.items():
            s_encrypted_text = encrypt_text(o_fernet_key, base64.b64decode(value).decode())
            s_encrypted_text_b64_encoded = base64.b64encode(s_encrypted_text.encode()).decode()
            s_decrypted_text = decrypt_text(o_fernet_key, base64.b64decode(s_encrypted_text_b64_encoded).decode())
            s_decrypted_text_b64_encoded = base64.b64encode(s_decrypted_text.encode()).decode()

            if s_decrypted_text_b64_encoded == value:
                o_secure_secret[-1]['spec']['data'].append({"key": key, "value": s_encrypted_text_b64_encoded})
            else:
                print(f"Original value: {value}")
                print(f"Decrypted value: {s_decrypted_text_b64_encoded}")
                exit("Something wrong with encryption! Please mail the administrator on redhu.sunny1994@gmail.com immediately.")

    s_temp_output_filename = 'secure_secrets.yaml'
    cleanup_file(s_temp_output_filename)

    with open(s_temp_output_filename, 'w') as file:
        try:
            yaml.dump_all(o_secure_secret, file, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)
    print()     # Empty line
    subprocess.run(f"cat {s_temp_output_filename}", shell=True, check=True)
    cleanup_file(s_temp_output_filename)

def decrypt_secure_secrets(o_fernet_key, l_secrets_to_decrypt):
    pass


def main():
    d_arguments = read_arguments()
    print(f"Arguments: {d_arguments}")
    init_k8s_client()

    o_cryption_secret, o_fernet_key = get_latest_cryption_secret(d_arguments["namespace"], d_arguments["encryptionsecret"])
    # print(f"cryption_secret: {cryption_secret}")

    if "text" in d_arguments:
        # Encrypt the provided text
        if d_arguments["method"] == "encrypt":
            s_encrypted_text = encrypt_text(o_fernet_key, d_arguments["text"])
            print(f"Encrypted value: {s_encrypted_text}")
        elif d_arguments["method"] == "decrypt":
            s_decrypted_text = decrypt_text(o_fernet_key, d_arguments["text"])
            print(f"Decrypted value: {s_decrypted_text}")
    elif "secret" in d_arguments:
        # Encrypt the provided secret
        if d_arguments["method"] == "encrypt":
            l_secrets_to_encrypt = list(filter(lambda x: d_arguments["secret"] in x.metadata.name, L_SECRETS_IN_NAMESPACE))
            encrypt_secrets(o_cryption_secret, o_fernet_key, l_secrets_to_encrypt)
        elif d_arguments["method"] == "decrypt":
            print("To be implemented!")
            pass
    else:
        # Encrypt all secrets in the given namespace
        if d_arguments["method"] == "encrypt":
            encrypt_secrets(o_cryption_secret, o_fernet_key, L_SECRETS_IN_NAMESPACE)
        elif d_arguments["method"] == "decrypt":
            print("To be implemented!")
            pass


main()

# Commands for testing:
# python3 kubectl-ssutils.py -n jenkins -e fernet-key -m encrypt -t "Hello world!"
# python3 kubectl-ssutils.py -n jenkins -e fernet-key -m decrypt -t "gAAAAABh0X5wMhFbxi6aSmIjR_ftPPMYGTOnfJkxF2Acytpw_8dBF81Ddk6kRB6xSFnfSfnzDRQpVpALRFhbyS3h5q9_bH4J3w=="
# python3 kubectl-ssutils.py -n jenkins -e fernet-key -m encrypt -s default
# python3 kubectl-ssutils.py -n jenkins -e fernet-key -m encrypt
