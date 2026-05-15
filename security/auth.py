# security/auth.py
import bcrypt

class AuthManager:
    def hash_master_password(self, master_password: str) -> bytes:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(master_password.encode('utf-8'), salt)
    
    def verify_master_password(self, input_password: str, stored_hash: bytes) -> bool:
        return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash)
    
    def save_master_hash(self, hashed_password: bytes):
        with open("master.key", "wb") as f:
            f.write(hashed_password)
    
    def load_master_hash(self) -> bytes | None:
        try:
            with open("master.key", "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None