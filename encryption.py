import rsa

def generate_key_pair():
    """
    Генерирует пару RSA ключей (публичный и приватный).
    Возвращает публичный и приватный ключи.
    """
    public_key, private_key = rsa.newkeys(2048)  # Длина ключа 2048 бит
    return public_key, private_key

def save_keys_to_file(public_key, private_key, public_key_file="public.pem", private_key_file="private.pem"):
    """
    Сохраняет публичный и приватный ключи в файлы.
    
    :param public_key: Публичный ключ.
    :param private_key: Приватный ключ.
    :param public_key_file: Имя файла для публичного ключа.
    :param private_key_file: Имя файла для приватного ключа.
    """
    try:
        with open(public_key_file, 'wb') as pub_file:
            pub_file.write(public_key.save_pkcs1('PEM'))

        with open(private_key_file, 'wb') as priv_file:
            priv_file.write(private_key.save_pkcs1('PEM'))

        print(f"Ключи успешно сохранены в файлы: {public_key_file}, {private_key_file}")
    except Exception as e:
        print(f"Ошибка при сохранении ключей: {e}")

def load_keys_from_file(public_key_file="public.pem", private_key_file="private.pem"):
    """
    Загружает публичный и приватный ключи из файлов.

    :param public_key_file: Имя файла для публичного ключа.
    :param private_key_file: Имя файла для приватного ключа.
    :return: Пара ключей (публичный и приватный) или None, если ошибка.
    """
    try:
        with open(public_key_file, 'rb') as pub_file:
            public_key = rsa.PublicKey.load_pkcs1(pub_file.read())

        with open(private_key_file, 'rb') as priv_file:
            private_key = rsa.PrivateKey.load_pkcs1(priv_file.read())

        return public_key, private_key

    except FileNotFoundError:
        print("Ошибка: Файл с ключами не найден.")
        return None, None
    except Exception as e:
        print(f"Ошибка при загрузке ключей: {e}")
        return None, None

def encrypt_message(message, public_key):
    """
    Шифрует сообщение с использованием публичного ключа.

    :param message: Сообщение для шифрования.
    :param public_key: Публичный ключ.
    :return: Зашифрованное сообщение.
    """
    try:
        encrypted_message = rsa.encrypt(message.encode('utf-8'), public_key)
        return encrypted_message
    except Exception as e:
        print(f"Ошибка при шифровании: {e}")
        return None

def decrypt_message(encrypted_message, private_key):
    """
    Расшифровывает сообщение с использованием приватного ключа.

    :param encrypted_message: Зашифрованное сообщение.
    :param private_key: Приватный ключ.
    :return: Расшифрованное сообщение.
    """
    try:
        decrypted_message = rsa.decrypt(encrypted_message, private_key).decode('utf-8')
        return decrypted_message
    except Exception as e:
        print(f"Ошибка при расшифровке: {e}")
        return None
