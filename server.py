import socket

UDP_MAX_SIZE = 65535
MAX_CLIENTS = 10

def listen(host: str = '0.0.0.0', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    members = {}  # Храним адреса и публичные ключи

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)
        msg = msg.decode('utf-8')

        if msg.startswith('__join__'):
            if addr not in members and len(members) < MAX_CLIENTS:
                # Сохраняем публичный ключ клиента
                client_key = msg[7:]
                members[addr] = client_key
                print(f'[+] Client {addr} joined.')

                # Уведомляем всех о новом участнике
                for member, key in members.items():
                    if member != addr:
                        # Используем двойное подчеркивание как разделитель
                        peer_msg = f"__peer__{member[0]}__{member[1]}__key__{key}"
                        s.sendto(peer_msg.encode('utf-8'), addr)
                        # Отправляем существующим клиентам информацию о новом
                        new_peer_msg = f"__peer__{addr[0]}__{addr[1]}__key__{client_key}"
                        s.sendto(new_peer_msg.encode('utf-8'), member)

if __name__ == '__main__':
    listen()