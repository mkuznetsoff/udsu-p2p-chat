import socket

UDP_MAX_SIZE = 65535
MAX_CLIENTS = 10

def listen(host: str = '0.0.0.0', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    members = set()

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)

        if msg.decode('utf-8') == '__join':
            if addr not in members and len(members) < MAX_CLIENTS:
                members.add(addr)
                print(f'[+] Client {addr} joined.')
                # Уведомляем всех о новом участнике
                for member in members:
                    if member != addr:
                        s.sendto(f"__peer {addr[0]} {addr[1]}".encode(), member)
                        s.sendto(f"__peer {member[0]} {member[1]}".encode(), addr)

if __name__ == '__main__':
    listen()