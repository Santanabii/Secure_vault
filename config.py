# config.py
APP_NAME = "SecureVault"
VERSION = "1.0"

# ====================== MongoDB Atlas ======================
MONGO_URI = "mongodb+srv://idontknowsantana:i6pHQ0j1z4BAvvos@cluster0.4aluwsj.mongodb.net/?retryWrites=true&w=majority"

DATABASE_NAME = "securevault_db"
CONNECTION_TIMEOUT = 15000

# ====================== Window Settings ======================
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650

# Security
MASTER_PASSWORD_MIN_LENGTH = 6
ENCRYPTION_SALT = b'SecureVaultSalt2025'