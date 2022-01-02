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
import getopt, sys, base64


def print_help():
    s_help = """
        Usage:
            kubectl-ssutils.py -n <namespace> -m <method> -s <secretname> [options]

            -h, --help                  Print help
            -n, --namespace             (required) namespace where the encryption key exists
            -m, --method                (required) Method to call; Valid values: encrypt, decrypt
            -s, --secretname            (required) name of the encryption secret; or an identifiable substring. Example: ssh-key
            -t, --text                  (optional) text to encrypt
    """

    print(s_help)
    exit()

def read_arguments():
    # Remove 1st argument from the list of command line arguments
    l_argumentList = sys.argv[1:]

    # Options
    s_options = "hn:m:s:t:"

    # Long options
    l_long_options = ["help", "namespace", "method", "secretname", "text"]

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
            elif s_currentArgument in ("-s", "--secretname"):
                d_arguments_result["secret"] = s_currentValue
            elif s_currentArgument in ("-t", "--text"):
                d_arguments_result["text"] = s_currentValue

        # Check required arguments
        if "namespace" in d_arguments_result and "method" in d_arguments_result and "secret" in d_arguments_result:
            return d_arguments_result
        else:
            print("Error: Missing required argument. Required arguments: namespace, method, secret")
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

    o_private_key = crypto_serialization.load_pem_private_key(
        data=base64.b64decode((o_latest_cryption_secret.data)["private_key"]),
        password=None,
        backend=crypto_default_backend()
    )

    o_public_key = crypto_serialization.load_ssh_public_key(
        data=base64.b64decode((o_latest_cryption_secret.data)["public_key"]),
        backend=crypto_default_backend()
    )

    return (o_latest_cryption_secret, o_private_key, o_public_key)

def encrypt(o_public_key, s_text):
    s_encrypted_text = o_public_key.encrypt(
        s_text.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return s_encrypted_text.decode(errors='replace')

def decrypt(o_private_key, s_text):
    s_decrypted_text = private_key.decrypt(
        s_text,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return s_decrypted_text


def main():
    d_arguments = read_arguments()
    print(f"Arguments: {d_arguments}")
    init_k8s_client()

    cryption_secret, o_private_key, o_public_key = get_latest_cryption_secret(d_arguments["namespace"], d_arguments["secret"])
    # print(f"cryption_secret: {cryption_secret}")

    if "text" in d_arguments:
        s_encrypted_text = encrypt(o_public_key, d_arguments["text"])
        # decrypt(o_private_key, text)
        print(f"Encrypted text: {s_encrypted_text}")


main()

# python3 kubectl-ssutils.py -n jenkins -s ssh-key -m encrypt -t "Hello world!"