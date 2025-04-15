import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QListWidget, QLabel
)
from PyQt5.QtCore import Qt
from client import P2PClient


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P Шифрованный Чат")
        self.setGeometry(300, 200, 500, 600)

        # UI
        self.chat_view = QListWidget()
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")

        self.send_button = QPushButton("Отправить всем")
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Чат:"))
        layout.addWidget(self.chat_view)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        self.setLayout(layout)

        # Клиент
        self.client = P2PClient(self.append_message)
        self.client.start()

    def append_message(self, msg: str):
        self.chat_view.addItem(msg)
        self.chat_view.scrollToBottom()

    def send_message(self):
        text = self.message_input.toPlainText().strip()
        if text:
            self.append_message(f"Вы → всем: {text}")
            self.client.send_to_all(text)
            self.message_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
