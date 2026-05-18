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

## Project Structure

```bash
SecureVault/
├── main.py
├── config.py
├── requirements.txt
├── master.key                 
├── user_profile.txt
├── database/
│   └── db_handler.py
├── security/
│   ├── auth.py
│   └── encryption.py
├── gui/
│   ├── login_window.py
│   ├── main_window.py
│   └── add_edit_window.py
└── README.md

Installation & Setup
1. Clone or Download the Project
2. Create Virtual Environment
Bashpython -m venv my-env
Activate Virtual Environment:

Windows (Command Prompt):Bashmy-env\Scripts\activate
Windows (Git Bash):Bashsource my-env/Scripts/activate

3. Install Dependencies
Bashpip install -r requirements.txt
4. Update MongoDB Connection
Open config.py and make sure your MONGO_URI is correct.
5. Run the Application
Bashpython main.py
How to Use
First Time Setup

Run the application
Enter a Username
Create a strong Master Password (minimum 8 characters with letters, numbers & symbols)
Click "Create New Account"
Restart and login with the same credentials

Main Features

Add New → Click the green button
Show Password → Select entry and click "Show Password"
Edit → Select entry and click "Edit"
Delete → Select entry and click "Delete"
Password Generator → Available in sidebar
Open Website → Double-click on any row with URL

Security Features

Master password is hashed using bcrypt
All passwords are encrypted using AES (Fernet)
Encryption key is derived from your Master Password
Each user’s data is isolated
No plain text passwords stored in database