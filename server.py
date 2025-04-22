import socket

UDP_MAX_SIZE = 65535
MAX_CLIENTS = 10

def listen(host: str = '0.0.0.0', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    members = {}

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)

        if msg == b'__request_keys':
            for member, key in members.items():
                if member != addr:
                    s.sendto(f"__peer {member[0]} {member[1]}".encode(), addr)
                    s.sendto(key, addr)
            continue

        if addr not in members and len(members) < MAX_CLIENTS:
            members[addr] = msg
            print(f'[+] Client {addr} joined.')
            # Уведомляем всех о новом участнике
            for member in members:
                if member != addr:
                    s.sendto(f"__peer {addr[0]} {addr[1]}".encode(), member)
                    s.sendto(msg, member)
            continue

        if addr not in members:
            print(f'[!] {addr} пытался подключиться, но достигнут лимит клиентов.')
            continue

        print(f'[*] Relaying message from {addr}')
        for member in members:
            if member != addr:
                s.sendto(msg, member)

if __name__ == '__main__':
    listen()
