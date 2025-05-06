import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QListWidget, QHBoxLayout, QMessageBox, QLabel,
    QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from client import P2PClient  # Подключи свой класс клиента

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P Чат — Telegram Style")
        self.setGeometry(100, 100, 800, 550)

        nickname, ok = QInputDialog.getText(self, 'Ввод ника', 'Введите ваш ник:')
        if not ok or not nickname:
            sys.exit()

        self.client = P2PClient(on_receive_callback=self.display_message, nickname=nickname)
        self.client.start()
        self.current_contact = None
        self.nicknames = {} # Dictionary to store nicknames

        self.setStyleSheet(self.load_stylesheet())

        # Основной виджет и компоненты
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay")

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Напишите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setObjectName("messageInput")

        self.send_button = QPushButton("➤")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedWidth(40)
        self.send_button.setObjectName("sendButton")

        self.contact_list = QListWidget()
        self.contact_list.setMaximumWidth(220)
        self.contact_list.setObjectName("contactList")
        self.contact_list.itemClicked.connect(self.select_contact)

        self.update_contacts_button = QPushButton("⟳")
        self.update_contacts_button.clicked.connect(self.update_contacts)
        self.update_contacts_button.setObjectName("updateButton")

        # Лейауты
        message_layout = QHBoxLayout()
        message_layout.addWidget(self.message_input)
        message_layout.addWidget(self.send_button)

        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(message_layout)

        contacts_layout = QVBoxLayout()
        contacts_layout.addWidget(QLabel("Контакты"))
        contacts_layout.addWidget(self.update_contacts_button)
        contacts_layout.addWidget(self.contact_list)

        main_layout = QHBoxLayout()
        main_layout.addLayout(contacts_layout)
        main_layout.addLayout(chat_layout)

        self.central_widget.setLayout(main_layout)

    def update_contacts(self):
        self.contact_list.clear()
        contacts = self.client.list_contacts()
        if not contacts:
            QMessageBox.information(self, "Контакты", "Нет доступных клиентов.")
        else:
            for contact in contacts:
                ip, port = contact.split(':')
                nickname = self.client.get_nickname((ip, int(port)))
                self.contact_list.addItem(nickname)
                self.nicknames[nickname] = contact


    def select_contact(self, item):
        nickname = item.text()
        self.current_contact = self.nicknames[nickname]
        self.display_message(f"[i] Вы выбрали: {nickname}")

    def display_message(self, message):
        self.chat_display.append(message)

    def send_message(self):
        text = self.message_input.text().strip()
        if not text or not self.current_contact:
            return
        ip, port = self.current_contact.split(':')
        self.client.send_to(ip, int(port), text)
        self.display_message(f"<b>Вы → {text}</b>")
        self.message_input.clear()

    def get_nickname(self, addr): # Placeholder - needs actual nickname resolution
        if addr in self.nicknames:
            return self.nicknames[addr]
        else:
            return f"{addr[0]}:{addr[1]}" # Fallback to IP:port if nickname not found


    def load_stylesheet(self):
        return """
        QWidget {
            background-color: #f8f8f8;
            font-family: "Segoe UI", sans-serif;
            font-size: 14px;
        }
        QTextEdit#chatDisplay {
            background-color: white;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
        }
        QLineEdit#messageInput {
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 8px;
        }
        QPushButton#sendButton {
            background-color: #0088cc;
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton#sendButton:hover {
            background-color: #007ab8;
        }
        QPushButton#updateButton {
            background-color: #e0e0e0;
            border: none;
            padding: 6px;
            font-size: 16px;
        }
        QListWidget#contactList {
            background-color: #ffffff;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QListWidget::item:selected {
            background-color: #d0efff;
        }
        QLabel {
            font-weight: bold;
            padding-bottom: 5px;
        }
        """

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()