from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from base64 import b64encode, b64decode
import os

class CryptoManager:
    def __init__(self, nickname=None):
        self.private_key = None
        self.public_key = None
        self.keys_file = None

        if nickname:
            # Определяем директорию для хранения ключей в зависимости от ОС
            if os.name == 'nt':  # Windows
                base_dir = os.path.join(os.getenv('APPDATA'), 'P2P-Chat')
            else:  # Linux/Unix
                base_dir = os.path.join(os.path.expanduser('~'), '.config', 'p2p-chat')
            
            # Создаем директорию если её нет
            os.makedirs(base_dir, mode=0o700, exist_ok=True)
            
            self.keys_file = os.path.join(base_dir, f'keys_{nickname}.pem')
            
            if os.path.exists(self.keys_file):
                # Загружаем существующий ключ
                with open(self.keys_file, 'rb') as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(),
                        password=None
                    )
            else:
                # Генерируем новую пару ключей
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                # Сохраняем ключ
                pem = self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                with open(self.keys_file, 'wb') as f:
                    f.write(pem)
        else:
            # Генерируем новую пару ключей без сохранения
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
        # Всегда создаем public_key из private_key
        if self.private_key:
            self.public_key = self.private_key.public_key()

    def get_public_key_str(self) -> str:
        if not self.public_key:
            raise ValueError("Public key not initialized")
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
        if not self.private_key:
            raise ValueError("Private key not initialized")
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
