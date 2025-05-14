import socket
import threading
import time
from crypto import CryptoManager
import os
import time
from colorama import init, Fore, Back, Style
import json
import zipfile

init(autoreset=True)  # Инициализация colorama

UDP_MAX_SIZE = 65535
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 3000


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    clear_screen()
    print(
        f"{Fore.CYAN}╔══════════════════════════════════════╗{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}║        P2P Защищенный Чат            ║{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}╚══════════════════════════════════════╝{Style.RESET_ALL}\n"
    )


def print_menu():
    print(f"\n{Fore.YELLOW}Команды:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}/list{Style.RESET_ALL} - список контактов")
    print(f"{Fore.GREEN}/change{Style.RESET_ALL} - сменить контакт")
    print(f"{Fore.GREEN}/clear{Style.RESET_ALL} - очистить экран")
    print(f"{Fore.GREEN}/exit{Style.RESET_ALL} - выход")
    print(
        f"{Fore.YELLOW}─────────────────────────────────────{Style.RESET_ALL}\n"
    )


class MessageHistory:

    def __init__(self, crypto_manager, nickname):
        self.crypto = crypto_manager
        self.nickname = nickname
        self.messages = []

    def add_message(self, sender, receiver, text):
        self.messages.append({
            'sender': sender,
            'receiver': receiver,
            'text': text
        })

    def encrypt_history(self):
        encrypted_messages = []
        for message in self.messages:
            encrypted_message = {
                'sender':
                self.crypto.encrypt(message['sender'],
                                     self.crypto.get_public_key_str()),
                'receiver':
                self.crypto.encrypt(message['receiver'],
                                     self.crypto.get_public_key_str()),
                'text':
                self.crypto.encrypt(message['text'],
                                     self.crypto.get_public_key_str())
            }
            encrypted_messages.append(encrypted_message)
        return encrypted_messages

    def decrypt_history(self, encrypted_messages):
        decrypted_messages = []
        for message in encrypted_messages:
            decrypted_message = {
                'sender':
                self.crypto.decrypt(message['sender']),
                'receiver':
                self.crypto.decrypt(message['receiver']),
                'text':
                self.crypto.decrypt(message['text'])
            }
            decrypted_messages.append(decrypted_message)
        return decrypted_messages

    def export_history(self, filename):
        encrypted_messages = self.encrypt_history()
        history_data = {
            'nickname': self.nickname,
            'public_key': self.crypto.get_public_key_str(),
            'messages': encrypted_messages
        }
        json_data = json.dumps(history_data)
        zip_filename = f"{filename}"
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("history.json", json_data)
        return zip_filename

    def import_history(self, filename):
        try:
            with zipfile.ZipFile(filename, 'r') as zipf:
                with zipf.open("history.json") as json_file:
                    json_data = json_file.read().decode('utf-8')
            history_data = json.loads(json_data)

            if history_data['nickname'] != self.nickname:
                print(
                    f"{Fore.RED}[!] Никнеймы не совпадают. Импорт невозможен.{Style.RESET_ALL}"
                )
                return False

            if history_data['public_key'] != self.crypto.get_public_key_str():
                print(
                    f"{Fore.RED}[!] Ключи шифрования не совпадают. Импорт невозможен.{Style.RESET_ALL}"
                )
                return False

            encrypted_messages = history_data['messages']
            self.messages = self.decrypt_history(encrypted_messages)
            print(f"{Fore.GREEN}[+] История успешно импортирована.{Style.RESET_ALL}")
            return True

        except Exception as e:
            print(f"{Fore.RED}[!] Ошибка при импорте истории: {e}{Style.RESET_ALL}")
            return False


class P2PClient:

    def __init__(self, on_receive_callback, nickname, server_host='0.0.0.0', server_port=3000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))
        self.contacts = {}  # {(ip, port): (public_key, nickname)}
        self.on_receive = on_receive_callback
        self.nickname = nickname
        self.crypto = CryptoManager(nickname)
        self.history = MessageHistory(self.crypto, self.nickname)
        self.server_host = server_host
        self.server_port = server_port

    def __del__(self):
        try:
            self.sock.sendto('__exit'.encode('utf-8'), (self.server_host, self.server_port))
            self.sock.close()
        except:
            pass

    def request_contacts_update(self):
        while True:
            try:
                self.sock.sendto(b'__request_keys', (SERVER_HOST, SERVER_PORT))
                time.sleep(10)  # Обновляем каждые 10 секунд
            except:
                break

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.request_contacts_update, daemon=True).start()
        join_msg = f"__join {self.crypto.get_public_key_str()} {self.nickname}"
        self.sock.sendto(join_msg.encode('utf-8'), (self.server_host, self.server_port))

    def listen(self):
        while True:
            try:
                msg, addr = self.sock.recvfrom(UDP_MAX_SIZE)
                msg = msg.decode('utf-8')

                if msg.startswith('__peer'):
                    _, ip, port, pub_key, nickname = msg.split(maxsplit=4)
                    self.contacts[(ip, int(port))] = (pub_key, nickname)
                    self.on_receive(f"[+] Обнаружен клиент {nickname}")
                elif msg.startswith('__leave'):
                    _, ip, port, nickname = msg.split(maxsplit=3)
                    addr = (ip, int(port))
                    if addr in self.contacts:
                        del self.contacts[addr]
                        self.on_receive(f"[-] Клиент {nickname} покинул чат")
                else:
                    try:
                        decrypted_msg = self.crypto.decrypt(msg)
                        nickname = self.get_nickname((addr[0], addr[1]))
                        sender_nickname = self.get_nickname((addr[0], addr[1]))
                        self.on_receive(f"<b>{nickname} → {decrypted_msg}</b>")
                        self.history.add_message(sender_nickname, self.nickname, decrypted_msg)
                    except Exception as e:
                        self.on_receive(
                            f"{Fore.RED}[!] Ошибка расшифровки: {e}{Style.RESET_ALL}"
                        )
            except Exception as e:
                self.on_receive(
                    f"{Fore.RED}[!] Ошибка при получении: {e}{Style.RESET_ALL}"
                )

    def list_contacts(self, with_ip=True):
        if with_ip:
            return [f"{ip}:{port}" for (ip, port) in self.contacts.keys()]
        return [self.contacts[addr][1] for addr in self.contacts.keys()]

    def get_nickname(self, addr):
        return self.contacts[addr][
            1] if addr in self.contacts else f"{addr[0]}:{addr[1]}"

    def send_to_all(self, text: str):
        for addr, pub_key in self.contacts.items():
            try:
                encrypted = self.crypto.encrypt(text, pub_key)
                self.sock.sendto(encrypted.encode('utf-8'), addr)
            except Exception as e:
                self.on_receive(
                    f"{Fore.RED}[Ошибка отправки {addr[0]}:{addr[1]}]: {e}{Style.RESET_ALL}"
                )

    def send_to(self, ip: str, port: int, text: str):
        addr = (ip, port)
        if addr not in self.contacts:
            self.on_receive(
                f"{Fore.RED}[!] Клиент {ip}:{port} не найден в списке контактов.{Style.RESET_ALL}"
            )
            return
        try:
            pub_key = self.contacts[addr][0]
            encrypted = self.crypto.encrypt(text, pub_key)
            self.sock.sendto(encrypted.encode('utf-8'), addr)
            # Сохраняем отправленное сообщение в историю
            recipient_nickname = self.contacts[addr][1]
            self.history.add_message(self.nickname, recipient_nickname, text)
        except Exception as e:
            self.on_receive(
                f"{Fore.RED}[Ошибка отправки {ip}:{port}]: {e}{Style.RESET_ALL}"
            )

    def export_history(self, directory: str) -> bool:
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(directory, f"chat_history_{timestamp}_{self.nickname}.zip")
            return self.history.export_history(filename)
        except Exception as e:
            print(f"Error during export: {e}")
            return False

    def import_history(self, filename: str) -> bool:
        try:
            return self.history.import_history(filename)
        except Exception as e:
            print(f"Error during import: {e}")
            return False


if __name__ == '__main__':
    messages = []

    print_header()
    nickname = input(f"{Fore.YELLOW}Введите ваш ник: {Style.RESET_ALL}")
    while not nickname or len(nickname) > 20:
        nickname = input(
            f"{Fore.RED}Ник должен быть от 1 до 20 символов: {Style.RESET_ALL}"
        )

    def print_messages():
        clear_screen()
        for message in messages[-10:]:  # Показываем последние 10 сообщений
            print(message)
        print("\n" + "─" * 50)  # Разделительная линия
        print(f"{Fore.CYAN}> {Style.RESET_ALL}", end='', flush=True)

    def handle_msg(msg):
        messages.append(msg)
        print_messages()

    client = P2PClient(on_receive_callback=handle_msg, nickname=nickname)
    client.start()

    def wait_for_contacts(timeout=5):
        print(f"{Fore.YELLOW}Поиск других участников...{Style.RESET_ALL}")
        for i in range(timeout):
            client.sock.sendto(b'__request_keys', (SERVER_HOST, SERVER_PORT))
            time.sleep(1)
            if client.list_contacts():
                return True
        return False

    def choose_contact():
        contacts = client.list_contacts()
        if not contacts:
            print(f"{Fore.RED}[!] Нет доступных клиентов.{Style.RESET_ALL}")
            return None
        print(f"\n{Fore.CYAN}Список доступных клиентов:{Style.RESET_ALL}")
        for i, contact in enumerate(contacts):
            print(f"{Fore.GREEN}[{i}]{Style.RESET_ALL} {contact}")
        while True:
            try:
                index = int(
                    input(
                        f"{Fore.YELLOW}Выберите номер контакта: {Style.RESET_ALL}"
                    ))
                return contacts[index]
            except (ValueError, IndexError):
                print(
                    f"{Fore.RED}[!] Неверный выбор. Попробуйте снова.{Style.RESET_ALL}"
                )

    print_header()

    while not wait_for_contacts():
        print(f"{Fore.RED}[!] Пока нет других участников.{Style.RESET_ALL}")
        choice = input(
            f"{Fore.YELLOW}Попробовать снова? (y/n): {Style.RESET_ALL}").lower(
            )
        if choice != 'y':
            print(f"{Fore.RED}Выход.{Style.RESET_ALL}")
            exit()
        print_header()

    current_contact = choose_contact()
    if not current_contact:
        print(f"{Fore.RED}[!] Контакт не выбран. Выход.{Style.RESET_ALL}")
        exit()

    ip, port = current_contact.split(':')
    port = int(port)

    print_header()
    print(
        f"{Fore.GREEN}Готово. Введите сообщение для отправки.{Style.RESET_ALL}"
    )
    print_menu()

    while True:
        try:
            msg = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
            if msg == "/exit":
                print(f"{Fore.YELLOW}Выход...{Style.RESET_ALL}")
                break
            elif msg == "/clear":
                messages.clear()
                print_header()
                print_menu()
            elif msg == "/list":
                print(
                    f"\n{Fore.YELLOW}Обновление списка клиентов...{Style.RESET_ALL}"
                )
                client.sock.sendto(b'__request_keys',
                                   (SERVER_HOST, SERVER_PORT))
                time.sleep(1)
                print(f"{Fore.CYAN}Доступные клиенты:{Style.RESET_ALL}")
                for contact in client.list_contacts():
                    print(f"{Fore.GREEN}- {contact}{Style.RESET_ALL}")
            elif msg == "/change":
                new_contact = choose_contact()
                if new_contact:
                    ip, port = new_contact.split(':')
                    port = int(port)
                    print(
                        f"{Fore.GREEN}[i] Переключено на {new_contact}{Style.RESET_ALL}"
                    )
            elif msg == "/export":
                filename = input(
                    f"{Fore.YELLOW}Введите имя файла для экспорта истории: {Style.RESET_ALL}"
                )
                exported_file = client.export_history(filename)
                print(
                    f"{Fore.GREEN}[+] История экспортирована в {exported_file}{Style.RESET_ALL}"
                )
            elif msg == "/import":
                filename = input(
                    f"{Fore.YELLOW}Введите имя файла для импорта истории: {Style.RESET_ALL}"
                )
                client.import_history(filename)
            elif msg:
                client.send_to(ip, port, msg)
                messages.append(f"{Fore.GREEN}Вы → {Style.RESET_ALL}{msg}")
                clear_screen()
                for message in messages[
                        -10:]:  # Показываем последние 10 сообщений
                    print(message)
                print("\n" + "─" * 50)  # Разделительная линия
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Выход...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[!] Ошибка: {e}{Style.RESET_ALL}")
