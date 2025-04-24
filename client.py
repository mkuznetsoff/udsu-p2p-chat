import socket
import threading
import rsa
import generate_key as genkey

UDP_MAX_SIZE = 65535
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 3000

class P2PClient:
    def __init__(self, on_receive_callback):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))

        self.contacts = {}  # (ip, port) -> rsa.PublicKey
        self.on_receive = on_receive_callback

        self.public_key, self.private_key = genkey.load_keys_from_file()
        if not self.public_key or not self.private_key:
            self.public_key, self.private_key = genkey.generate_key_pair()
            genkey.save_keys_to_file(self.public_key, self.private_key)

        self.sock.sendto(self.public_key.save_pkcs1('PEM'), (SERVER_HOST, SERVER_PORT))

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        self.sock.sendto(b'__request_keys', (SERVER_HOST, SERVER_PORT))

    def listen(self):
        while True:
            msg, addr = self.sock.recvfrom(UDP_MAX_SIZE)
            try:
                if msg.startswith(b'__peer'):
                    _, ip, port = msg.decode().split()
                    self.contacts[(ip, int(port))] = None  # ключ будет позже
                    self.on_receive(f"[+] Обнаружен клиент {ip}:{port}")
                    continue

                try:
                    pubkey = rsa.PublicKey.load_pkcs1(msg)
                    self.contacts[addr] = pubkey
                    self.on_receive(f"[+] Получен публичный ключ от {addr[0]}:{addr[1]}")
                except:
                    decrypted_msg = rsa.decrypt(msg, self.private_key).decode('utf-8')
                    self.on_receive(f"{addr[0]}:{addr[1]} → {decrypted_msg}")
            except Exception as e:
                self.on_receive(f"[!] Ошибка при получении: {e}")

    def list_contacts(self):
        return [f"{ip}:{port}" for (ip, port) in self.contacts]

    def send_to_all(self, text: str):
        for addr, pubkey in self.contacts.items():
            if pubkey is not None:
                try:
                    encrypted_msg = rsa.encrypt(text.encode('utf-8'), pubkey)
                    self.sock.sendto(encrypted_msg, addr)
                except Exception as e:
                    self.on_receive(f"[Ошибка отправки {addr[0]}:{addr[1]}]: {e}")

    def send_to(self, ip: str, port: int, text: str):
        addr = (ip, port)
        if addr not in self.contacts or self.contacts[addr] is None:
            self.sock.sendto(b'__request_keys', (SERVER_HOST, SERVER_PORT))
            self.on_receive(f"[!] Ключ для {ip}:{port} ещё не получен")
            return
        try:
            encrypted_msg = rsa.encrypt(text.encode('utf-8'), self.contacts[addr])
            self.sock.sendto(encrypted_msg, addr)
        except Exception as e:
            self.on_receive(f"[Ошибка отправки {ip}:{port}]: {e}")

if __name__ == '__main__':
    import time

    def handle_msg(msg):
        print(msg)

    client = P2PClient(on_receive_callback=handle_msg)
    client.start()

    def wait_for_contacts(timeout=5):
        for i in range(timeout):
            client.sock.sendto(b'__request_keys', (SERVER_HOST, SERVER_PORT))
            time.sleep(1)
            if client.list_contacts():
                return True
        return False

    def choose_contact():
        contacts = client.list_contacts()
        if not contacts:
            print("[!] Нет доступных клиентов.")
            return None
        print("\nСписок доступных клиентов:")
        for i, contact in enumerate(contacts):
            print(f"[{i}] {contact}")
        while True:
            try:
                index = int(input("Выберите номер контакта: "))
                return contacts[index]
            except (ValueError, IndexError):
                print("[!] Неверный выбор. Попробуйте снова.")

    # Ожидание доступных клиентов
    while not wait_for_contacts():
        print("[!] Пока нет других участников.")
        choice = input("Попробовать снова? (y/n): ").lower()
        if choice != 'y':
            print("Выход.")
            exit()

    current_contact = choose_contact()
    if not current_contact:
        print("[!] Контакт не выбран. Выход.")
        exit()

    ip, port = current_contact.split(':')
    port = int(port)

    print("\nГотово. Введите сообщение для отправки.")
    print("Команды: /list - список, /change - сменить контакт, /exit - выйти")

    while True:
        msg = input("> ").strip()
        if msg == "/exit":
            print("Выход...")
            break
        elif msg == "/list":
            print("\nОбновление списка клиентов...")
            client.sock.sendto(b'__request_keys', (SERVER_HOST, SERVER_PORT))
            time.sleep(1)
            for contact in client.list_contacts():
                print(f"- {contact}")
        elif msg == "/change":
            new_contact = choose_contact()
            if new_contact:
                ip, port = new_contact.split(':')
                port = int(port)
                print(f"[i] Переключено на {new_contact}")
        else:
            client.send_to(ip, port, msg)
