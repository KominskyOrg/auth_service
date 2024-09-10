from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

def decrypt_password(encrypted_password, secret_key):
    encrypted_password_bytes = base64.b64decode(encrypted_password)
    iv = encrypted_password_bytes[:16]
    encrypted_password_bytes = encrypted_password_bytes[16:]
    cipher = Cipher(algorithms.AES(secret_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_password = decryptor.update(encrypted_password_bytes) + decryptor.finalize()
    return decrypted_password.rstrip(b"\0").decode('utf-8')