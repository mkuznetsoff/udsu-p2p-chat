import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QListWidget,
                             QHBoxLayout, QMessageBox, QLabel, QInputDialog,
                             QFileDialog, QDialog, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

class ExportWorker(QThread):
    finished = pyqtSignal()
    success = pyqtSignal()
    error = pyqtSignal()
    
    def __init__(self, client, directory):
        super().__init__()
        self.client = client
        self.directory = directory
        
    def run(self):
        try:
            if self.client.export_history(self.directory):
                self.success.emit()
            else:
                self.error.emit()
        except Exception:
            self.error.emit()
        finally:
            self.finished.emit()
from PyQt5.QtGui import QFont, QColor, QPalette
from client import P2PClient, SERVER_HOST, SERVER_PORT  # Импортируем константы


class ChatWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("UDSU P2P CHAT")
        self.setGeometry(100, 100, 800, 550)
        
        # Register QTextCursor for threading
        from PyQt5.QtCore import qRegisterMetaType
        qRegisterMetaType('QTextCursor')
        
        nickname, ok = QInputDialog.getText(self, 'Ввод ника',
                                            'Введите ваш ник:')
        if not ok or not nickname:
            sys.exit()

        # Создаем диалог выбора сервера
        server_dialog = QDialog(self)
        server_dialog.setWindowTitle("Выбор сервера")
        layout = QVBoxLayout()
        
        combo = QComboBox()
        combo.addItems(["0.0.0.0:3000", "smartcontrol.su:3000", "Другой сервер"])
        layout.addWidget(combo)
        
        custom_input = QLineEdit()
        custom_input.setPlaceholderText("Адрес:порт")
        custom_input.hide()
        layout.addWidget(custom_input)
        
        def on_combo_changed(text):
            custom_input.setVisible(text == "Другой сервер")
        
        combo.currentTextChanged.connect(on_combo_changed)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Отмена")
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        
        server_dialog.setLayout(layout)
        
        def on_ok():
            server_dialog.accept()
        
        def on_cancel():
            server_dialog.reject()
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(on_cancel)
        
        if server_dialog.exec_() != QDialog.Accepted:
            sys.exit()
            
        # Получаем выбранный адрес сервера
        selected = combo.currentText()
        if selected == "0.0.0.0:3000":
            server_host, server_port = "0.0.0.0", 3000
        elif selected == "smartcontrol.su:3000":
            server_host, server_port = "smartcontrol.su", 3000
        else:
            custom_addr = custom_input.text().split(":")
            if len(custom_addr) != 2:
                QMessageBox.critical(self, "Ошибка", "Неверный формат адреса")
                sys.exit()
            server_host, server_port = custom_addr[0], int(custom_addr[1])

        self.client = P2PClient(on_receive_callback=self.display_message,
                              nickname=nickname,
                              server_host=server_host,
                              server_port=server_port)
        self.client.start()
        self.current_contact = None
        self.nicknames = {}  # Dictionary to store nicknames

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
        
        # Кнопки экспорта/импорта
        buttons_layout = QHBoxLayout()
        self.export_button = QPushButton("Экспорт")
        self.import_button = QPushButton("Импорт")
        self.export_button.setObjectName("historyButton")
        self.import_button.setObjectName("historyButton")
        self.export_button.clicked.connect(self.export_history)
        self.import_button.clicked.connect(self.import_history)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.import_button)
        contacts_layout.addLayout(buttons_layout)
        
        # Таймер для автообновления контактов
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_contacts)
        self.refresh_timer.start(5000)  # Обновление каждые 5 секунд

        main_layout = QHBoxLayout()
        main_layout.addLayout(contacts_layout)
        main_layout.addLayout(chat_layout)

        self.central_widget.setLayout(main_layout)
        self.closeEvent = self.handle_close


    def update_contacts(self):
        self.contact_list.clear()
        contacts = self.client.list_contacts()
        if not contacts:
            QMessageBox.information(self, "Контакты",
                                    "Нет доступных клиентов.")
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
        # Используем invokeMethod для потокобезопасного обновления GUI
        from PyQt5.QtCore import Qt, QMetaObject
        QMetaObject.invokeMethod(self.chat_display, 
                               "append",
                               Qt.QueuedConnection,
                               Q_ARG(str, message))

    def send_message(self):
        text = self.message_input.text().strip()
        if not text or not self.current_contact:
            return
        ip, port = self.current_contact.split(':')
        self.client.send_to(ip, int(port), text)
        self.display_message(f"<b>Вы → {text}</b>")
        self.message_input.clear()

    def get_nickname(self, addr):
        if addr in self.nicknames:
            return self.nicknames[addr]
        else:
            return f"{addr[0]}:{addr[1]}"  # Fallback to IP:port if nickname not found

    def export_history(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку для экспорта")
        if directory:
            # Создаем отдельный поток для экспорта
            self.export_thread = QThread()
            self.export_worker = ExportWorker(self.client, directory)
            self.export_worker.moveToThread(self.export_thread)
            
            self.export_thread.started.connect(self.export_worker.run)
            self.export_worker.finished.connect(self.export_thread.quit)
            self.export_worker.finished.connect(self.export_worker.deleteLater)
            self.export_thread.finished.connect(self.export_thread.deleteLater)
            self.export_worker.success.connect(self.on_export_success)
            self.export_worker.error.connect(self.on_export_error)
            
            self.export_thread.start()
            self.export_button.setEnabled(False)
            
    def on_export_success(self):
        self.export_button.setEnabled(True)
        QMessageBox.information(self, "Успех", "История успешно экспортирована")
        
    def on_export_error(self):
        self.export_button.setEnabled(True)
        QMessageBox.warning(self, "Ошибка", "Не удалось экспортировать историю")

    def import_history(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Импорт истории", "", "ZIP Files (*.zip)")
        if filename:
            if self.client.import_history(filename):
                # Показываем импортированные сообщения в чате
                for msg in self.client.history.messages:
                    self.display_message(f"{msg['sender']} → {msg['text']}")
                QMessageBox.information(self, "Успех", "История успешно импортирована")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось импортировать историю")

    def handle_close(self, event):
        """Обработка закрытия окна"""
        try:
            if self.client:
                print("[i] Отключение от сервера...")
                self.client.sock.sendto('__exit'.encode(), (SERVER_HOST, SERVER_PORT))
                # Даем серверу время на обработку
                time.sleep(0.5)
                self.client.sock.close()
                print("[+] Успешное отключение")
        except Exception as e:
            print(f"[-] Ошибка при отключении: {e}")
        event.accept()

    def load_stylesheet(self):
        return """
        QWidget {
            background-color: #f8f8f8;
            font-family: "Segoe UI", sans-serif;
            font-size: 14px;
        }
        QPushButton#historyButton {
            background-color: #0088cc;
            color: white;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton#historyButton:hover {
            background-color: #007ab8;
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
