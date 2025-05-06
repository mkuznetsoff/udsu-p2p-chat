
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
import os
import json

class CryptoManager:
    def __init__(self, nickname):
        self.nickname = nickname
        self.storage_dir = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), '.p2pchat')
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.keys_file = os.path.join(self.storage_dir, f'{nickname}_keys.enc')
        self.history_file = os.path.join(self.storage_dir, f'{nickname}_history.enc')
        
        if os.path.exists(self.keys_file):
            self._load_keys()
        else:
            self._generate_new_keys()
            
        # Generate history encryption key
        self.history_key = Fernet.generate_key()
        self.fernet = Fernet(self.history_key)

    def _generate_new_keys(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self._save_keys()

    def _save_keys(self):
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(self.keys_file, 'wb') as f:
            f.write(private_pem)

    def _load_keys(self):
        with open(self.keys_file, 'rb') as f:
            private_pem = f.read()
        self.private_key = serialization.load_pem_private_key(private_pem, password=None)
        self.public_key = self.private_key.public_key()

    def save_chat_history(self, history):
        encrypted_data = self.fernet.encrypt(json.dumps(history).encode())
        with open(self.history_file, 'wb') as f:
            f.write(encrypted_data)

    def load_chat_history(self):
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data)
        except:
            return []

    def get_public_key_str(self) -> str:
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return b64encode(pem).decode('utf-8')

    def load_public_key_str(self, key_str: str):
        pem = b64decode(key_str)
        return serialization.load_pem_public_key(pem)

    def encrypt(self, message: str, public_key_str: str) -> str:
        public_key = self.load_public_key_str(public_key_str)
        encrypted = public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_message: str) -> str:
        encrypted = b64decode(encrypted_message)
        decrypted = self.private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')
