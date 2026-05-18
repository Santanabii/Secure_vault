# main.py
import customtkinter as ctk
import tkinter as tk

# Fix for DPI Scaling Error
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Optional: Try to fix high DPI issues
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    login_window = LoginWindow()
    
    def on_successful_login(username: str, master_password: str):
        print(f"Login Successful! Welcome, {username}")
        try:
            app = MainWindow(master_password)
            app.run()
        except Exception as e:
            print("Error opening main window:", e)
    
    login_window.on_login_success = on_successful_login
    login_window.run()


if __name__ == "__main__":
    main()