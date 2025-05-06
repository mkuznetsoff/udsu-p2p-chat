
import socket

UDP_MAX_SIZE = 65535
MAX_CLIENTS = 10

def listen(host: str = '0.0.0.0', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    members = {}  # {addr: (public_key, nickname)}

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)
        msg = msg.decode('utf-8')

        if msg == '__exit':
            if addr in members:
                nickname = members[addr][1]
                del members[addr]
                print(f'[-] Client {nickname} ({addr}) left.')
                
        elif msg.startswith('__join'):
            if addr not in members and len(members) < MAX_CLIENTS:
                _, public_key, nickname = msg.split(maxsplit=2)
                members[addr] = (public_key, nickname)
                print(f'[+] Client {nickname} ({addr}) joined.')
                # Уведомляем всех о новом участнике
                for member in members:
                    if member != addr:
                        # Отправляем информацию о новом клиенте существующим
                        s.sendto(f"__peer {addr[0]} {addr[1]} {public_key} {nickname}".encode(), member)
                        # Отправляем информацию о существующих клиентах новому
                        mem_key, mem_nick = members[member]
                        s.sendto(f"__peer {member[0]} {member[1]} {mem_key} {mem_nick}".encode(), addr)

if __name__ == '__main__':
    listen()
