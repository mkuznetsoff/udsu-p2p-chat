
import socket

UDP_MAX_SIZE = 65535
MAX_CLIENTS = 10

def listen(host: str = '0.0.0.0', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'[SERVER] Listening at {host}:{port}')
    print('[SERVER] Waiting for clients...')

    members = {}  # {addr: (public_key, nickname)}

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)
        msg = msg.decode('utf-8')

        if msg == '__exit':
            if addr in members:
                nickname = members[addr][1]
                print(f'\n[-] Клиент {nickname} ({addr[0]}:{addr[1]}) покинул чат')
                # Уведомляем всех об уходе клиента
                for member in members:
                    if member != addr:
                        leave_msg = f"__leave {addr[0]} {addr[1]} {nickname}"
                        s.sendto(leave_msg.encode(), member)
                        print(f'[>] Отправлено уведомление о выходе к {members[member][1]}')
                del members[addr]
                active_users = ", ".join([members[m][1] for m in members])
                print(f'[i] Активные пользователи: {active_users if active_users else "нет"}')
                
        elif msg.startswith('__join'):
            if addr not in members and len(members) < MAX_CLIENTS:
                _, public_key, nickname = msg.split(maxsplit=2)
                members[addr] = (public_key, nickname)
                print(f'\n[+] Клиент {nickname} ({addr}) присоединился к чату')
                print(f'[i] Активные пользователи: {", ".join([members[m][1] for m in members])}')
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
