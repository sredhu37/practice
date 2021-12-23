# from cryptography.hazmat.primitives import serialization as crypto_serialization
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.fernet import Fernet

def create_fernet_key():
    key_str = Fernet.generate_key()
    return key_str.decode()


def encrypt_using_fernet_key(key_str, text_to_encrypt):
    fernet = Fernet(key_str.encode())
    encrypted_text = fernet.encrypt(text_to_encrypt.encode())
    return encrypted_text.decode()


def decrypt_using_fernet_key(key_str, encrypted_text):
    fernet = Fernet(key_str.encode())
    decrypted_text = fernet.decrypt(encrypted_text.encode())
    return decrypted_text.decode()


# ======================= The below snippets are just for testing. Remove them after testing. =========================

# f_key_str = create_fernet_key()
# print(f"f_key_str: {f_key_str}")
# encrypted_text = encrypt_using_fernet_key(f_key_str, "Hello world-123!")
# print(f"encrypted_text: {encrypted_text}")
# decrypted_text = decrypt_using_fernet_key(f_key_str, encrypted_text)
# print(f"decrypted_text: {decrypted_text}")
