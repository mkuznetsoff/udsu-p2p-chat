# server.py
import socket
import json

UDP_MAX_SIZE = 65535
members = {}  # addr -> public_key

def listen(host='0.0.0.0', port=3000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'Listening at {host}:{port}')

    while True:
        msg, addr = s.recvfrom(UDP_MAX_SIZE)

        if msg.startswith(b'__register__'):
            public_key = msg[len(b'__register__'):]
            members[addr] = public_key
            print(f'Registered {addr}')
        elif msg == b'__request_peers__':
            peers_info = [{'ip': ip, 'port': port, 'key': members[(ip, port)].decode()} for (ip, port) in members if (ip, port) != addr]
            s.sendto(json.dumps(peers_info).encode(), addr)
