from cryptography.fernet import Fernet

# key = Fernet.generate_key()
key = b'JekyBivdoFl0zR2nKLA9O9QUmxXPPRaQB_yA3pcf9oA='
print(key)
f = Fernet(key)

# encrypted_text = f.encrypt(b'Hello world')
# print(f"encrypted_text: {encrypted_text}")

encrypted_text = b'gAAAAABh0W1VdB3H_ZEPFVl0prbHyAuzwNR1X8npslr8ANsrhlZX-sJgVWWzmARojKQtb0LQX5qW_W6p3pTa1ZkoC_-va4G42w=='
decrypted_text = f.decrypt(encrypted_text)
print(f"decrypted_text: {decrypted_text}")
