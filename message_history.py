
from datetime import datetime
import json
import zipfile
from crypto import CryptoManager

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

    def export_history(self, filename: str) -> bool:
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
            return False

    def import_history(self, filename: str) -> bool:
        try:
            with zipfile.ZipFile(filename, 'r') as zf:
                encrypted_data = zf.read('history.enc').decode('utf-8')
            
            # Расшифровываем данные
            json_data = self.crypto.decrypt(encrypted_data)
            data = json.loads(json_data)
            
            # Проверяем соответствие
            if data['nickname'] != self.nickname:
                print("Nickname mismatch")
                return False
            
            if data['public_key'] != self.crypto.get_public_key_str():
                print("Public key mismatch")
                return False
                
            self.messages = data['messages']
            return True
        except Exception as e:
            print(f"Error importing history: {e}")
            return False
