
import rsa
import pickle
import base64

def generate_keys(bits=2048):
    """Генерирует пару RSA ключей"""
    return rsa.newkeys(bits)

def serialize_key(key):
    """Сериализует ключ в строку base64"""
    return base64.b64encode(pickle.dumps(key)).decode('utf-8')

def deserialize_key(key_str):
    """Десериализует ключ из строки base64"""
    return pickle.loads(base64.b64decode(key_str.encode('utf-8')))

def encrypt_message(message: str, public_key) -> str:
    """Шифрует сообщение с помощью публичного ключа"""
    return base64.b64encode(rsa.encrypt(message.encode('utf-8'), public_key)).decode('utf-8')

def decrypt_message(encrypted_message: str, private_key) -> str:
    """Расшифровывает сообщение с помощью приватного ключа"""
    try:
        decrypted = rsa.decrypt(base64.b64decode(encrypted_message.encode('utf-8')), private_key)
        return decrypted.decode('utf-8')
    except:
        return None
