# gui/login_window.py
import customtkinter as ctk
from tkinter import messagebox
import re
from security.auth import AuthManager
from config import APP_NAME, MASTER_PASSWORD_MIN_LENGTH


class LoginWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} - Login")
        self.root.geometry("480x520")
        self.root.resizable(False, False)
        
        self.auth = AuthManager()
        self.setup_ui()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        ctk.CTkLabel(self.root, text=APP_NAME, font=ctk.CTkFont(size=32, weight="bold")).pack(pady=30)
        ctk.CTkLabel(self.root, text="Secure Password Manager", font=ctk.CTkFont(size=16)).pack(pady=(0, 30))

        ctk.CTkLabel(self.root, text="Username", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=70)
        self.username_entry = ctk.CTkEntry(self.root, width=340, height=45, placeholder_text="Enter username")
        self.username_entry.pack(pady=(5, 15))

        ctk.CTkLabel(self.root, text="Master Password", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=70)
        self.password_entry = ctk.CTkEntry(self.root, width=340, height=45, placeholder_text="Enter master password", show="*")
        self.password_entry.pack(pady=(5, 20))

        ctk.CTkButton(self.root, text="Login", width=340, height=50, font=ctk.CTkFont(size=16, weight="bold"),
                     command=self.login).pack(pady=10)

        ctk.CTkButton(self.root, text="Create New Account", width=340, height=40, fg_color="transparent", border_width=2,
                     command=self.set_master_password).pack(pady=8)

    def is_strong_password(self, password):
        if len(password) < MASTER_PASSWORD_MIN_LENGTH: return False
        if not re.search(r"[A-Za-z]", password): return False
        if not re.search(r"[0-9]", password): return False
        if not re.search(r"[@$!%*#?&^_+=]", password): return False
        return True

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill both fields")
            return

        stored_hash = self.auth.load_master_hash()
        if not stored_hash:
            messagebox.showwarning("No Account", "Please create an account first")
            return

        if self.auth.verify_master_password(password, stored_hash):
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.root.destroy()
            self.on_login_success(username, password)
        else:
            messagebox.showerror("Failed", "Incorrect credentials!")

    def set_master_password(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Both fields are required")
            return

        if not self.is_strong_password(password):
            messagebox.showwarning("Weak Password", "Password must contain letters, numbers and symbols (min 8 chars)")
            return

        hashed = self.auth.hash_master_password(password)
        self.auth.save_master_hash(hashed)

        with open("user_profile.txt", "w", encoding="utf-8") as f:
            f.write(username)

        messagebox.showinfo("Success", f"Account created for {username}!\nYou can now login.")

    def on_login_success(self, username: str, master_password: str):
        pass

    def run(self):
        self.root.mainloop()