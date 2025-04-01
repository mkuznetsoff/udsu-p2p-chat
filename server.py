# сервер
import socket

UDP_MAX_SIZE = 65535

def listen(host: str = '127.0.0.1', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    members = {}
    
    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)

        if addr not in members:
            try:
                members[addr] = msg
                print(f'Client {addr} joined and sent public key')
                # Рассылаем новый ключ всем участникам
                for member in members:
                    if member != addr:
                        s.sendto(msg, member)
                continue
            except:
                continue
        
        if msg == b'__request_keys':
            # Отправляем запрошенные ключи
            for member, key in members.items():
                if member != addr:
                    s.sendto(key, addr)
            continue
        
        print(f'Relaying encrypted message from {addr}')
        for member in members:
            if member == addr:
                continue
            s.sendto(msg, member)

if __name__ == '__main__':
    listen()
