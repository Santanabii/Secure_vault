# Secure_vault
# SecureVault - Personal Password Manager
A secure, modern desktop password manager built with Python.

## Features
- Master Password protection
- AES Encryption for all saved passwords
- Store unlimited passwords (Website, Username, Password, Category)
- Clean and modern user interface (CustomTkinter)
- MongoDB Atlas cloud database
- Add, View, and Delete passwords
- Local data encryption (passwords are never stored in plain text)

## Tech Stack
- **Python**
- **CustomTkinter** (GUI)
- **MongoDB Atlas** (Database)
- **PyMongo** (Database driver)
- **Cryptography** (Encryption)
- **Bcrypt** (Master password hashing)

## Project Structure
SecureVault/
├── main.py
├── config.py
├── database/
├── security/
├── gui/
├── master.key         
└── README.md


## How to Run

1. Clone or download the project
2. Create virtual environment:
   ```bash
   python -m venv my-env
   my-env\Scripts\activate