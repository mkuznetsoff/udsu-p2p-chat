
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from base64 import b64encode, b64decode

import json
import os

class CryptoManager:
    def __init__(self):
        # Генерируем пару ключей RSA
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        self.history_file = "chat_history.enc"
        self.chat_history = self.load_chat_history()

    def save_message_to_history(self, message):
        self.chat_history.append(message)
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.chat_history, f)
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_chat_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
        return []

    def import_history(self, file_path):
        try:
            with open(file_path, 'r') as f:
                self.chat_history = json.load(f)
            with open(self.history_file, 'w') as f:
                json.dump(self.chat_history, f)
            return True
        except Exception as e:
            print(f"Error importing history: {e}")
            return False

    def export_history(self, file_path):
        try:
            with open(file_path, 'w') as f:
                json.dump(self.chat_history, f)
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False

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
