from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import padding as padding_asym
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def serialize_pub(public_key_pem):
    public_key = serialization.load_pem_public_key(
    public_key_pem,
    backend=default_backend()
    )
    return public_key

def decrypt_data_asym(private_key, encrypted_data):
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data


def encrypt_data_asym(public_key, data):
    if type(data) == type(""):
        data = data.encode()
    elif type(data) != type("") and type(data) != type(b""):
        data = b"Error: sorry something went wrong on the server side."
    encrypted_data = public_key.encrypt(
    data,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
        )
    )
    return encrypted_data

def gen_keys_asym():
    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    # Serialize public key to PEM format
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, public_key_pem


def encrypt_data_sym(key, data):
    iv = os.urandom(16)  # Generate a new IV each message
    padder = padding_asym.PKCS7(algorithms.AES.block_size).padder()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    padded_data = padder.update(data) + padder.finalize()
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv, encrypted_data
    
def decrypt_data_sym(key, iv, encrypted_data):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Unpad the decrypted plaintext
    unpadder = padding_asym.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return decrypted_data