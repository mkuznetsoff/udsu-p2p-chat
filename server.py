# p2p_key_server.py
import socket

UDP_MAX_SIZE = 65535

def listen(host: str = '127.0.0.1', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    members = {}  # addr -> public_key

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)

        if msg == b'__request_keys':
            # Клиент запросил ключи всех других участников
            for member, key in members.items():
                if member != addr:
                    s.sendto(key, addr)
            continue

        # Предполагаем, что это публичный ключ нового клиента
        if addr not in members:
            members[addr] = msg
            print(f'[+] Зарегистрирован клиент {addr}, отправлен публичный ключ')

            # Рассылаем его ключ другим клиентам
            for member in members:
                if member != addr:
                    s.sendto(msg, member)
        else:
            print(f'[!] Неизвестное сообщение от {addr}, проигнорировано')

if __name__ == '__main__':
    listen()
