
import socket
import time
import os
from datetime import datetime

UDP_MAX_SIZE = 65535
MAX_CLIENTS = 10

def listen(host: str = '0.0.0.0', port: int = 3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'[SERVER] Listening at {host}:{port}')
    print('[SERVER] Waiting for clients...')

    members = {}  # {addr: (public_key, nickname)}
    last_activity = {}  # {addr: timestamp}
    TIMEOUT = 30  # seconds

    while True:
        try:
            msg, addr = s.recvfrom(UDP_MAX_SIZE)
            msg = msg.decode('utf-8')
            current_time = time.time()
            
            # Используем адрес, с которого пришел запрос
            client_ip = addr[0]
            if client_ip.startswith('192.168.') or client_ip.startswith('10.') or client_ip.startswith('172.'):
                client_ip = s.getsockname()[0]  # Используем IP сервера
            
            # Обновляем время последней активности
            if addr in members:
                last_activity[addr] = current_time
            
            # Проверяем таймауты
            disconnected = []
            for member_addr in list(members.keys()):
                if current_time - last_activity.get(member_addr, 0) > TIMEOUT:
                    disconnected.append(member_addr)
            
            # Обрабатываем отключившихся пользователей
            for disc_addr in disconnected:
                if disc_addr in members:
                    nickname = members[disc_addr][1]
                    print(f'\n[-] Клиент {nickname} ({disc_addr[0]}:{disc_addr[1]}) отключен по таймауту')
                    for member in members:
                        if member != disc_addr:
                            leave_msg = f"__leave {disc_addr[0]} {disc_addr[1]} {nickname}"
                            s.sendto(leave_msg.encode(), member)
                    del members[disc_addr]
                    del last_activity[disc_addr]

            if msg == '__exit':
                if addr in members:
                    nickname = members[addr][1]
                    print(f'\n[-] Клиент {nickname} ({addr[0]}:{addr[1]}) покинул чат')
                    for member in members:
                        if member != addr:
                            leave_msg = f"__leave {addr[0]} {addr[1]} {nickname}"
                            s.sendto(leave_msg.encode(), member)
                    del members[addr]
                    if addr in last_activity:
                        del last_activity[addr]
                    
            elif msg.startswith('__join'):
                if addr not in members and len(members) < MAX_CLIENTS:
                    _, public_key, nickname = msg.split(maxsplit=2)
                    members[addr] = (public_key, nickname)
                    last_activity[addr] = current_time
                    print(f'\n[+] Клиент {nickname} ({addr[0]}:{addr[1]}) присоединился к чату')
                    
                    # Уведомляем всех о новом участнике
                    for member in members:
                        if member != addr:
                            s.sendto(f"__peer {addr[0]} {addr[1]} {public_key} {nickname}".encode(), member)
                            mem_key, mem_nick = members[member]
                            s.sendto(f"__peer {member[0]} {member[1]} {mem_key} {mem_nick}".encode(), addr)
            
            # Очищаем экран и выводим состояние
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'\n[SERVER] Listening at {host}:{port}')
            active_users = ", ".join([members[m][1] for m in members])
            print(f'[i] Активные пользователи: {active_users if active_users else "нет"}')
            
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == '__main__':
    listen()
