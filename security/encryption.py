# security/encryption.py
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionManager:
    def __init__(self, master_password: str):
        self.key = self._derive_key(master_password)
        self.fernet = Fernet(self.key)
    
    def _derive_key(self, master_password: str):
        """Derive encryption key from master password"""
        salt = b'SecureVaultSalt2025'   # Keep this consistent
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt password"""
        return self.fernet.encrypt(plaintext.encode('utf-8')).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt password"""
        return self.fernet.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')