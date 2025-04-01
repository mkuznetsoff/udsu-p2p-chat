
import socket
import threading
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QLineEdit,
    QLabel, QWidget, QStackedWidget, QListWidget, QTextEdit, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

UDP_MAX_SIZE = 65535

class Client:
    def __init__(self, host='192.168.150.139', port=3000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self.host, self.port))
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            msg = self.socket.recv(UDP_MAX_SIZE)
            decoded_msg = msg.decode('ascii')
            self.on_message_received(decoded_msg)

    def send_message(self, msg):
        self.socket.send(msg.encode('ascii'))

    def join_chat(self):
        self.socket.send('__join'.encode('ascii'))

    def on_message_received(self, message):
        pass  # Будет переопределен в GUI для обновления чата

class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P Chat App")
        self.setGeometry(100, 100, 400, 600)

        self.client = Client()  # Создаем экземпляр клиента

        # Подключаем метод обновления чата
        self.client.on_message_received = self.update_chat_area

        self.main_widget = QStackedWidget()
        self.setCentralWidget(self.main_widget)

        self.init_first_login()
        self.init_empty_main_screen()
        self.init_chat_screen()
        self.init_settings_screen()

    def init_first_login(self):
        first_login = QWidget()
        layout = QVBoxLayout()

        label = QLabel("First Login")
        label.setFont(QFont("Arial", 18))
        label.setAlignment(Qt.AlignCenter)

        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter username")

        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.goto_empty_main_screen)

        layout.addWidget(label)
        layout.addWidget(username_input)
        layout.addWidget(continue_button)
        first_login.setLayout(layout)
        self.main_widget.addWidget(first_login)

    def init_empty_main_screen(self):
        empty_screen = QWidget()
        layout = QVBoxLayout()

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search chats...")

        create_chat_button = QPushButton("Create Chat")
        create_chat_button.clicked.connect(self.goto_create_chat)

        join_chat_button = QPushButton("Join Chat")
        join_chat_button.clicked.connect(self.goto_join_chat)

        layout.addWidget(search_bar)
        layout.addWidget(create_chat_button)
        layout.addWidget(join_chat_button)
        empty_screen.setLayout(layout)
        self.main_widget.addWidget(empty_screen)

    def init_chat_screen(self):
        chat_screen = QWidget()
        layout = QVBoxLayout()

        self.chat_list = QListWidget()
        self.chat_list.addItem("Chat 1")
        self.chat_list.addItem("Chat 2")

        self.message_area = QTextEdit()
        self.message_area.setPlaceholderText("Write a message...")

        send_button = QPushButton("Send")
        send_button.setMaximumHeight(30)
        send_button.clicked.connect(self.send_message)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.message_area)
        bottom_layout.addWidget(send_button)

        layout.addWidget(self.chat_list)
        layout.addLayout(bottom_layout)

        chat_screen.setLayout(layout)
        self.main_widget.addWidget(chat_screen)

    def init_settings_screen(self):
        settings_screen = QWidget()
        layout = QVBoxLayout()

        username_label = QLabel("Username")
        username_input = QLineEdit()

        import_button = QPushButton("Import from .zip")
        export_button = QPushButton("Export to .zip")

        layout.addWidget(username_label)
        layout.addWidget(username_input)
        layout.addWidget(import_button)
        layout.addWidget(export_button)

        settings_screen.setLayout(layout)
        self.main_widget.addWidget(settings_screen)

    def goto_empty_main_screen(self):
        self.main_widget.setCurrentIndex(1)
        self.client.join_chat()  # Присоединяемся к чату

    def goto_create_chat(self):
        print("Create chat clicked")

    def goto_join_chat(self):
        print("Join chat clicked")

    def send_message(self):
        message = self.message_area.toPlainText()
        if message:
            self.client.send_message(message)  # Отправляем сообщение через клиент
            self.message_area.clear()

    def update_chat_area(self, message):
        # Обновляем текстовую область с сообщениями
        self.message_area.append(message)


if __name__ == "__main__":
    app = QApplication([])
    window = ChatApp()
    window.show()
    app.exec_()
