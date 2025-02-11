from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QLineEdit,
    QLabel, QWidget, QStackedWidget, QListWidget, QTextEdit, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat App")
        self.setGeometry(100, 100, 400, 600)

        self.main_widget = QStackedWidget()
        self.setCentralWidget(self.main_widget)

        self.init_first_login()
        self.init_empty_main_screen()
        self.init_chat_screen()
        self.init_settings_screen()

    def init_first_login(self):
        """First Login Screen"""
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
        """Empty Main Screen"""
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
        """Chat Screen"""
        chat_screen = QWidget()
        layout = QVBoxLayout()

        chat_list = QListWidget()
        chat_list.addItem("Chat 1")
        chat_list.addItem("Chat 2")

        message_area = QTextEdit()
        message_area.setPlaceholderText("Write a message...")

        send_button = QPushButton("Send")
        send_button.setMaximumHeight(30)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(message_area)
        bottom_layout.addWidget(send_button)

        layout.addWidget(chat_list)
        layout.addLayout(bottom_layout)

        chat_screen.setLayout(layout)
        self.main_widget.addWidget(chat_screen)

    def init_settings_screen(self):
        """Settings Screen"""
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

    def goto_create_chat(self):
        print("Create chat clicked")

    def goto_join_chat(self):
        print("Join chat clicked")


if __name__ == "__main__":
    app = QApplication([])
    window = ChatApp()
    window.show()
    app.exec_()
