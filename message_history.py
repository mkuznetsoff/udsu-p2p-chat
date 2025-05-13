
import json
import zipfile
import os
from datetime import datetime
from crypto import CryptoManager
from base64 import b64encode, b64decode

class MessageHistory:
    def __init__(self, crypto_manager: CryptoManager, nickname: str):
        self.crypto = crypto_manager
        self.nickname = nickname
        self.messages = []
        
    def add_message(self, sender: str, recipient: str, message: str):
        self.messages.append({
            'timestamp': datetime.now().isoformat(),
            'sender': sender,
            'recipient': recipient,
            'message': message
        })

    def export_history(self, filename: str):
        try:
            if not self.messages:
                print("No messages to export")
                return False
                
            # Сериализуем сообщения
            data = {
                'nickname': self.nickname,
                'public_key': self.crypto.get_public_key_str(),
                'messages': self.messages
            }
            
            # Шифруем данные
            json_data = json.dumps(data)
            encrypted_data = self.crypto.encrypt(json_data, self.crypto.get_public_key_str())
            
            # Создаем ZIP архив
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('history.enc', encrypted_data)
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return Falseory.enc', encrypted_data)
        return True

    def import_history(self, filename: str) -> bool:
        try:
            with zipfile.ZipFile(filename, 'r') as zf:
                encrypted_data = zf.read('history.enc').decode('utf-8')
                
            # Расшифровываем данные
            json_data = self.crypto.decrypt(encrypted_data)
            data = json.loads(json_data)
            
            # Проверяем соответствие ключей и ника
            if data['nickname'] != self.nickname or data['public_key'] != self.crypto.get_public_key_str():
                return False
                
            self.messages.extend(data['messages'])
            return True
        except Exception as e:
            print(f"Error importing history: {e}")
            return False
