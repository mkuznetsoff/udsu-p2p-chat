
import socket

UDP_MAX_SIZE = 65535
MAX_CLIENTS = 10

def listen(host: str = '0.0.0.0', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    members = {}  # {addr: public_key}

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)
        msg = msg.decode('utf-8')

        if msg.startswith('__join'):
            if addr not in members and len(members) < MAX_CLIENTS:
                _, public_key = msg.split(maxsplit=1)
                members[addr] = public_key
                print(f'[+] Client {addr} joined.')
                # Уведомляем всех о новом участнике
                for member in members:
                    if member != addr:
                        # Отправляем информацию о новом клиенте существующим
                        s.sendto(f"__peer {addr[0]} {addr[1]} {public_key}".encode(), member)
                        # Отправляем информацию о существующих клиентах новому
                        s.sendto(f"__peer {member[0]} {member[1]} {members[member]}".encode(), addr)

if __name__ == '__main__':
    listen()
