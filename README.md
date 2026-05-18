# Secure_vault
# SecureVault - Personal Password Manager

A secure and modern desktop password manager built with Python for the end-of-module project.

## Features

- **Master Password Protection** with strong password validation
- **User Account System** (Each user sees only their own passwords)
- **AES Encryption** for all stored passwords
- **Add, View, Edit, and Delete** passwords
- **Clickable URLs** (double-click to open website)
- **Copy Username & Password** to clipboard
- **Strong Password Generator**
- **Real-time Password Strength Indicator**
- **Clean Modern UI** using CustomTkinter
- **Cloud Database** (MongoDB Atlas)

## Tech Stack

- **Python 3**
- **CustomTkinter** - Modern GUI
- **MongoDB Atlas** - Cloud Database
- **PyMongo** - Database Driver
- **Cryptography (Fernet)** - Password Encryption
- **Bcrypt** - Master Password Hashing
- **Pyperclip** - Copy to clipboard

 
## Features
1. Master Password with strong validation
2. User account isolation (each user sees only their data)
3. Encryption for all passwords
4. Add, Edit, Delete, and View passwords
5. Clickable URLs (double-click to open)
6. Copy Username & Password
7. Strong Password Generator with real-time strength indicator
8. Clean modern UI using CustomTkinter
9. MongoDB Atlas cloud database


## Installation & Setup
1. Create Virtual Environment
```bash
 python -m venv my-env
2. Activate Virtual Environment
Windows (Command Prompt):
```bash
my-env\Scripts\activate

3. Install Dependencies
```bash
pip install -r requirements.txt
4. Configure MongoDB
Update your MONGO_URI in config.py with your Atlas connection string.
5. Run the Application
```bash
python main.py

## How to Use

First Time: Enter username and create a strong master password → Click "Create New Account"
Restart the app and login
Use the sidebar to navigate
Double-click any row to open the website
Use "Show Password", "Edit", or "Delete" buttons


## Security Features

Master password hashed with bcrypt
All passwords encrypted with AES (Fernet)
Encryption key derived from master password
Data isolated per user

