
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from base64 import b64encode, b64decode

class CryptoManager:
    def __init__(self):
        # Генерируем пару ключей RSA
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_str(self) -> str:
        # Сериализуем публичный ключ в формат PEM
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return b64encode(pem).decode('utf-8')

    def load_public_key_str(self, key_str: str):
        # Загружаем публичный ключ из строки
        pem = b64decode(key_str)
        return serialization.load_pem_public_key(pem)

    def encrypt(self, message: str, public_key_str: str) -> str:
        # Шифруем сообщение публичным ключом получателя
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
        # Расшифровываем сообщение своим приватным ключом
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
