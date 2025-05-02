import socket
import threading

UDP_MAX_SIZE = 65535
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 3000

from crypto_utils import generate_keys, serialize_key, deserialize_key, encrypt_message, decrypt_message

class P2PClient:
    def __init__(self, on_receive_callback):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))
        self.contacts = {}  # Храним адреса и публичные ключи
        self.on_receive = on_receive_callback
        # Генерируем ключи при создании клиента
        self.public_key, self.private_key = generate_keys()

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        # Регистрируемся на сервере с публичным ключом
        join_msg = f"__join__{serialize_key(self.public_key)}"
        self.sock.sendto(join_msg.encode('utf-8'), (SERVER_HOST, SERVER_PORT))

    def listen(self):
        while True:
            try:
                msg, addr = self.sock.recvfrom(UDP_MAX_SIZE)
                msg = msg.decode('utf-8')

                if msg.startswith('__peer'):
                    try:
                        parts = msg.split('__')
                        if len(parts) >= 5:
                            _, ip, port_str, _, key = parts[0:5]  # Добавляем пропуск метки 'key'
                            try:
                                port = int(port_str)
                                peer_key = deserialize_key(key)
                                self.contacts[(ip, port)] = peer_key
                                self.on_receive(f"[+] Обнаружен клиент {ip}:{port}")
                            except ValueError as e:
                                self.on_receive(f"[!] Ошибка обработки порта: {e}")
                        else:
                            self.on_receive("[!] Неверный формат сообщения о пире")
                    except Exception as e:
                        self.on_receive(f"[!] Ошибка обработки информации о пире: {e}")
                elif msg.startswith('__msg__'):
                    # Расшифровываем сообщение
                    encrypted = msg[6:]
                    decrypted = decrypt_message(encrypted, self.private_key)
                    if decrypted:
                        self.on_receive(f"{addr[0]}:{addr[1]} → {decrypted}")
                    else:
                        self.on_receive(f"[!] Ошибка расшифровки сообщения от {addr[0]}:{addr[1]}")
            except Exception as e:
                self.on_receive(f"[!] Ошибка при получении: {e}")

    def list_contacts(self):
        return [f"{ip}:{port}" for (ip, port) in self.contacts]

    def send_to_all(self, text: str):
        for addr, pub_key in self.contacts.items():
            try:
                encrypted = encrypt_message(text, pub_key)
                message = f"__msg__{encrypted}"
                self.sock.sendto(message.encode('utf-8'), addr)
            except Exception as e:
                self.on_receive(f"[Ошибка отправки {addr[0]}:{addr[1]}]: {e}")

    def send_to(self, ip: str, port: int, text: str):
        addr = (ip, port)
        if addr not in self.contacts:
            self.on_receive(f"[!] Клиент {ip}:{port} не найден в списке контактов.")
            return
        try:
            # Получаем публичный ключ получателя
            pub_key = self.contacts[addr]
            # Шифруем сообщение
            encrypted = encrypt_message(text, pub_key)
            if encrypted:
                message = f"__msg__{encrypted}"
                self.sock.sendto(message.encode('utf-8'), addr)
            else:
                self.on_receive("[!] Ошибка шифрования сообщения")
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
                contact = contacts[index]
                try:
                    ip, port_str = contact.split(':')
                    port = int(port_str)
                    return (ip, port)
                except ValueError as e:
                    print(f"[!] Неверный формат адреса: {e}")
                    return None
            except (ValueError, IndexError):
                print("[!] Неверный выбор. Попробуйте снова.")
                return None

    # Ожидание доступных клиентов
    while not wait_for_contacts():
        print("[!] Пока нет других участников.")
        choice = input("Попробовать снова? (y/n): ").lower()
        if choice != 'y':
            print("Выход.")
            exit()

    contact_info = choose_contact()
    if not contact_info:
        print("[!] Контакт не выбран. Выход.")
        exit()

    ip, port = contact_info

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