import socket
import threading
from crypto import CryptoManager
import os
import time
from colorama import init, Fore, Back, Style

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


class P2PClient:

    def __init__(self, on_receive_callback, nickname):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))
        self.contacts = {}  # {(ip, port): (public_key, nickname)}
        self.on_receive = on_receive_callback
        self.nickname = nickname
        self.crypto = CryptoManager(nickname)
        self.chat_history = self.crypto.load_chat_history()

    def start(self):
        threading.Thread(target=self.listen, daemon=True).start()
        join_msg = f"__join {self.crypto.get_public_key_str()} {self.nickname}"
        self.sock.sendto(join_msg.encode('utf-8'), (SERVER_HOST, SERVER_PORT))

    def listen(self):
        while True:
            try:
                msg, addr = self.sock.recvfrom(UDP_MAX_SIZE)
                msg = msg.decode('utf-8')

                if msg.startswith('__peer'):
                    _, ip, port, pub_key, nickname = msg.split(maxsplit=4)
                    self.contacts[(ip, int(port))] = (pub_key, nickname)
                    self.on_receive(f"[+] Обнаружен клиент {nickname}")
                else:
                    try:
                        decrypted_msg = self.crypto.decrypt(msg)
                        nickname = self.get_nickname((addr[0], addr[1]))
                        message = f"<b>{nickname} → {decrypted_msg}</b>"
                        self.chat_history.append(message)
                        self.crypto.save_chat_history(self.chat_history)
                        self.on_receive(message)
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
            pub_key = self.contacts[addr][
                0]  # Get just the public key from the tuple
            encrypted = self.crypto.encrypt(text, pub_key)
            self.sock.sendto(encrypted.encode('utf-8'), addr)
            message = f"<b>Вы → {text}</b>"
            self.chat_history.append(message)
            self.crypto.save_chat_history(self.chat_history)
        except Exception as e:
            self.on_receive(
                f"{Fore.RED}[Ошибка отправки {ip}:{port}]: {e}{Style.RESET_ALL}"
            )


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
