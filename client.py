# клиент
import socket
import threading
import os
import generate_key as genkey
import rsa

UDP_MAX_SIZE = 65535

# Загрузка или генерация ключей
public_key, private_key = genkey.load_keys_from_file()
if not public_key or not private_key:
    public_key, private_key = genkey.generate_key_pair()
    genkey.save_keys_to_file(public_key, private_key)

def listen(s: socket.socket, contacts: dict):
    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)
        try:
            decrypted_msg = rsa.decrypt(msg, private_key).decode('utf-8')
            print(f'\r\rMessage from {addr}: {decrypted_msg}\n' + f'you: ', end='')
        except:
            try:
                contacts[addr] = rsa.PublicKey.load_pkcs1(msg)
                print(f'\r\rReceived public key from {addr}\n' + f'you: ', end='')
            except:
                print('\r\r[Ошибка расшифровки]\n' + f'you: ', end='')

def connect(host: str = '127.0.0.1', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(public_key.save_pkcs1('PEM'), (host, port))
    
    contacts = {}
    threading.Thread(target=listen, args=(s, contacts), daemon=True).start()
    
    # Запрашиваем список участников
    s.sendto(b'__request_keys', (host, port))
    
    while True:
        recipient = input("Enter recipient address (IP:PORT) or 'all': ")
        msg = input(f'you: ')
        
        if recipient == 'all':
            if not contacts:
                print("[Ошибка] Нет доступных контактов для отправки.")
                continue
            for addr in contacts:
                encrypted_msg = rsa.encrypt(msg.encode('utf-8'), contacts[addr])
                s.sendto(encrypted_msg, addr)
        elif ':' in recipient:
            try:
                ip, port = recipient.split(':')
                addr = (ip, int(port))
                if addr in contacts:
                    encrypted_msg = rsa.encrypt(msg.encode('utf-8'), contacts[addr])
                    s.sendto(encrypted_msg, addr)
                else:
                    print("[Ошибка] Указанный получатель не в контактах.")
            except ValueError:
                print("[Ошибка] Неверный формат адреса. Введите IP:PORT.")
        else:
            print("[Ошибка] Неверный формат ввода. Введите IP:PORT или 'all'.")

if __name__ == '__main__':
    os.system('clear')
    print('Welcome to encrypted chat!')
    connect()
