
import os
import json
from pathlib import Path
from crypto import CryptoManager
from base64 import b64encode, b64decode

class HistoryManager:
    def __init__(self, nickname: str, crypto_manager: CryptoManager):
        self.nickname = nickname
        self.crypto_manager = crypto_manager
        self.history_dir = self._get_history_dir()
        os.makedirs(self.history_dir, exist_ok=True)
    
    def _get_history_dir(self) -> Path:
        if os.name == 'nt':  # Windows
            base_dir = Path(os.getenv('APPDATA')) / 'P2PChat'
        else:  # Linux/Mac
            base_dir = Path.home() / '.p2pchat'
        return base_dir / 'history'
    
    def _get_chat_filename(self, peer_nickname: str) -> Path:
        safe_name = f"{self.nickname}_{peer_nickname}.chat"
        return self.history_dir / safe_name
    
    def save_message(self, peer_nickname: str, message: str, is_outgoing: bool):
        filename = self._get_chat_filename(peer_nickname)
        entry = {
            'timestamp': str(int(time.time())),
            'message': message,
            'is_outgoing': is_outgoing
        }
        
        # Encrypt the entry
        encrypted_data = self.crypto_manager.encrypt(
            json.dumps(entry),
            self.crypto_manager.get_public_key_str()
        )
        
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(encrypted_data + '\n')
    
    def load_history(self, peer_nickname: str) -> list:
        filename = self._get_chat_filename(peer_nickname)
        messages = []
        
        if not filename.exists():
            return messages
            
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    decrypted = self.crypto_manager.decrypt(line.strip())
                    entry = json.loads(decrypted)
                    messages.append(entry)
                except Exception as e:
                    print(f"Error decrypting message: {e}")
                    
        return sorted(messages, key=lambda x: x['timestamp'])
