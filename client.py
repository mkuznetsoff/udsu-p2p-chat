# client.py
import socket
import threading
import json
import rsa
import generate_key as genkey

UDP_MAX_SIZE = 65535
SERVER_HOST = 'smartcontrol.su'
SERVER_PORT = 3000

class P2PClient:
    def __init__(self, on_receive_callback):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))  # автоматический выбор порта

        self.contacts = {}  # (ip, port) -> public_key
        self.on_receive = on_receive_callback

        # Загрузка или генерация ключей
        self.public_key, self.private_key = genkey.load_keys_from_file()
        if not self.public_key or not self.private_key:
            self.public_key, self.private_key = genkey.generate_key_pair()
            genkey.save_keys_to_file(self.public_key, self.private_key)

        # Регистрация на сервере
        self.sock.sendto(b'__register__' + self.public_key.save_pkcs1('PEM'), (SERVER_HOST, SERVER_PORT))

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        self.request_peers()

    def request_peers(self):
        self.sock.sendto(b'__request_peers__', (SERVER_HOST, SERVER_PORT))
        msg, _ = self.sock.recvfrom(UDP_MAX_SIZE)
        peers_info = json.loads(msg.decode())
        for peer in peers_info:
            ip = peer['ip']
            port = peer['port']
            key = rsa.PublicKey.load_pkcs1(peer['key'].encode())
            self.contacts[(ip, port)] = key
            # Отправляем пустое сообщение для открытия NAT
            self.sock.sendto(b'ping', (ip, port))

    def listen(self):
        while True:
            msg, addr = self.sock.recvfrom(UDP_MAX_SIZE)
            if msg == b'ping':
                continue  # Игнорируем ping-сообщения
            try:
                decrypted_msg = rsa.decrypt(msg, self.private_key).decode('utf-8')
                self.on_receive(f"{addr[0]}:{addr[1]} → {decrypted_msg}")
            except:
                self.on_receive("[!] Ошибка расшифровки сообщения")

    def send_to_all(self, text: str):
        if not self.contacts:
            self.on_receive("[!] Нет получателей.")
            return
        for addr, pubkey in self.contacts.items():
            try:
                encrypted_msg = rsa.encrypt(text.encode('utf-8'), pubkey)
                self.sock.sendto(encrypted_msg, addr)
            except Exception as e:
                self.on_receive(f"[Ошибка отправки {addr[0]}:{addr[1]}]: {e}")
