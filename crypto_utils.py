
import rsa
import pickle
import base64

def generate_keys(bits=2048):
    """Генерирует пару RSA ключей"""
    try:
        return rsa.newkeys(bits)
    except Exception as e:
        print(f"Ошибка генерации ключей: {e}")
        return None, None

def serialize_key(key):
    """Сериализует ключ в строку base64"""
    try:
        pickled = pickle.dumps(key)
        # Убеждаемся что длина соответствует требованиям base64
        encoded = base64.urlsafe_b64encode(pickled)
        return encoded.decode('utf-8')
    except Exception as e:
        print(f"Ошибка сериализации: {e}")
        return None

def deserialize_key(key_str):
    """Десериализует ключ из строки base64"""
    try:
        # Добавляем padding если необходимо
        padding = 4 - (len(key_str) % 4)
        if padding != 4:
            key_str += '=' * padding
        decoded = base64.urlsafe_b64decode(key_str.encode('utf-8'))
        return pickle.loads(decoded)
    except Exception as e:
        print(f"Ошибка десериализации: {e}")
        return None

def encrypt_message(message: str, public_key) -> str:
    """Шифрует сообщение с помощью публичного ключа"""
    try:
        if not public_key:
            raise ValueError("Публичный ключ отсутствует")
        encrypted = rsa.encrypt(message.encode('utf-8'), public_key)
        encoded = base64.urlsafe_b64encode(encrypted)
        return encoded.decode('utf-8')
    except Exception as e:
        print(f"Ошибка шифрования: {e}")
        return None

def decrypt_message(encrypted_message: str, private_key) -> str:
    """Расшифровывает сообщение с помощью приватного ключа"""
    try:
        if not private_key:
            raise ValueError("Приватный ключ отсутствует")
        # Добавляем padding если необходимо
        padding = 4 - (len(encrypted_message) % 4)
        if padding != 4:
            encrypted_message += '=' * padding
        decoded = base64.urlsafe_b64decode(encrypted_message.encode('utf-8'))
        decrypted = rsa.decrypt(decoded, private_key)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Ошибка расшифровки: {e}")
        return None
