import rsa
import os
import qrcode

def generate_key_pair():
    """Генерирует пару RSA ключей (приватный и открытый).

    Returns:
        tuple: Пара ключей (открытый ключ, приватный ключ).
    """
    (public_key, private_key) = rsa.newkeys(2048)  # Длина ключа: 2048 бит
    return public_key, private_key

def save_keys_to_file(public_key, private_key, public_key_file="public.pem", private_key_file="private.pem"):
    """Сохраняет открытый и приватный ключи в файлы.

    Args:
        public_key: Открытый ключ.
        private_key: Приватный ключ.
        public_key_file (str, optional): Имя файла для открытого ключа. Defaults to "public.pem".
        private_key_file (str, optional): Имя файла для приватного ключа. Defaults to "private.pem".
    """
    try:
        with open(public_key_file, 'wb') as f:
            f.write(public_key.save_pkcs1('PEM'))  # Сохраняем открытый ключ в формате PEM

        with open(private_key_file, 'wb') as f:
            f.write(private_key.save_pkcs1('PEM')) # Сохраняем приватный ключ в формате PEM

        print(f"Ключи успешно сохранены в файлы:\n  Открытый ключ: {public_key_file}\n  Приватный ключ: {private_key_file}")

    except Exception as e:
        print(f"Ошибка при сохранении ключей в файлы: {e}")

def load_keys_from_file(public_key_file="public.pem", private_key_file="private.pem"):
  """Загружает открытый и приватный ключи из файлов.

  Args:
      public_key_file (str, optional): Имя файла для открытого ключа. Defaults to "public.pem".
      private_key_file (str, optional): Имя файла для приватного ключа. Defaults to "private.pem".

  Returns:
      tuple: Пара ключей (открытый ключ, приватный ключ), или (None, None) в случае ошибки.
  """
  try:
      with open(public_key_file, 'rb') as f:
          public_key = rsa.PublicKey.load_pkcs1(f.read())

      with open(private_key_file, 'rb') as f:
          private_key = rsa.PrivateKey.load_pkcs1(f.read())

      return public_key, private_key

  except FileNotFoundError:
      print("Ошибка: Файл ключа не найден.")
      return None, None
  except Exception as e:
      print(f"Ошибка при загрузке ключей: {e}")
      return None, None


# --- Main ---
if __name__ == "__main__":
    # 1. Генерация пары ключей
    public_key, private_key = generate_key_pair()

    # 2. Сохранение ключей в файлы (рекомендуется)
    save_keys_to_file(public_key, private_key)

    # 3. Пример загрузки ключей из файлов (для демонстрации)
    loaded_public_key, loaded_private_key = load_keys_from_file()

    if loaded_public_key and loaded_private_key:
        print("Ключи успешно загружены из файлов.")
        # Здесь можно использовать загруженные ключи
        # Например, зашифровать сообщение открытым ключом и расшифровать приватным.

        message = "савасднемрождения<3".encode('utf-8')  # Сообщение в байтах

        # Шифруем сообщение открытым ключом
        encrypted_message = rsa.encrypt(message, loaded_public_key)
        print("Зашифрованное сообщение:", encrypted_message)

        # Расшифровываем сообщение приватным ключом
        decrypted_message = rsa.decrypt(encrypted_message, loaded_private_key).decode('utf-8')
        print("Расшифрованное сообщение:", decrypted_message)
    else:
        print("Загрузка ключей не удалась.")


# Данные, которые будут закодированы в QR-код
data = message 

# Создание QR-кода
qr = qrcode.QRCode(
    version=1,  # Версия QR-кода (1-40, None для автоматического определения)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Уровень коррекции ошибок (L, M, Q, H)
    box_size=10,  # Размер каждого "пикселя" QR-кода
    border=4,  # Толщина границы вокруг QR-кода
)

qr.add_data(data)
qr.make(fit=True)

# Создание изображения QR-кода
img = qr.make_image(fill_color="black", back_color="white")

# Сохранение изображения в файл
img.save("example.png")

print("QR-код успешно создан и сохранен в файл example.png")
