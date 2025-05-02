
import rsa
import pickle
import base64

def generate_keys(bits=2048):
    """Генерирует пару RSA ключей"""
    return rsa.newkeys(bits)

def serialize_key(key):
    """Сериализует ключ в строку base64"""
    try:
        pickled = pickle.dumps(key)
        # Добавляем дополнительное кодирование для избежания проблем с форматированием
        return base64.urlsafe_b64encode(pickled).decode('utf-8')
    except Exception as e:
        print(f"Ошибка сериализации: {e}")
        return None

def deserialize_key(key_str):
    """Десериализует ключ из строки base64"""
    try:
        # Используем urlsafe_b64decode для более надежного декодирования
        decoded = base64.urlsafe_b64decode(key_str.encode('utf-8'))
        return pickle.loads(decoded)
    except Exception as e:
        print(f"Ошибка десериализации: {e}")
        return None

def encrypt_message(message: str, public_key) -> str:
    """Шифрует сообщение с помощью публичного ключа"""
    try:
        encrypted = rsa.encrypt(message.encode('utf-8'), public_key)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"Ошибка шифрования: {e}")
        return None

def decrypt_message(encrypted_message: str, private_key) -> str:
    """Расшифровывает сообщение с помощью приватного ключа"""
    try:
        decoded = base64.urlsafe_b64decode(encrypted_message.encode('utf-8'))
        decrypted = rsa.decrypt(decoded, private_key)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Ошибка расшифровки: {e}")
        return None
