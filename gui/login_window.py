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
        self.root.geometry("460x600")
        self.root.resizable(False, False)
        
        self.auth = AuthManager()
        self.setup_ui()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        title = ctk.CTkLabel(self.root, text=APP_NAME, font=ctk.CTkFont(size=32, weight="bold"))
        title.pack(pady=25)

        subtitle = ctk.CTkLabel(self.root, text="Secure Password Manager", 
                               font=ctk.CTkFont(size=16))
        subtitle.pack(pady=(0, 30))

        # Username
        ctk.CTkLabel(self.root, text="Username", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=70)
        self.username_entry = ctk.CTkEntry(self.root, placeholder_text="Enter username", 
                                         width=320, height=45)
        self.username_entry.pack(pady=(5, 15))

        # Master Password
        ctk.CTkLabel(self.root, text="Master Password", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=70)
        self.password_entry = ctk.CTkEntry(self.root, placeholder_text="Create strong master password", 
                                         show="*", width=320, height=45)
        self.password_entry.pack(pady=(5, 20))

        # Login Button
        ctk.CTkButton(self.root, text="Login", width=320, height=50, 
                     font=ctk.CTkFont(size=16, weight="bold"),
                     command=self.login).pack(pady=10)

        # Create Account Button
        ctk.CTkButton(self.root, text="Create New Account", width=320, height=40,
                     fg_color="transparent", border_width=2,
                     command=self.set_master_password).pack(pady=8)

        # Password Requirements Note
        note = ctk.CTkLabel(self.root, text="Master Password must contain:\n"
                                           "• At least 8 characters\n"
                                           "• Letters, Numbers & Symbols",
                           font=ctk.CTkFont(size=12), text_color="gray")
        note.pack(pady=15)

    #  Password strength checking function
    def is_strong_password(self, password: str) -> bool:
        """Check if password meets strength requirements"""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Za-z]", password):      # Contains letter
            return False
        if not re.search(r"[0-9]", password):         # Contains number
            return False
        if not re.search(r"[@$!%*#?&^_+=]", password):  # Contains symbol
            return False
        return True

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please fill both fields")
            return

        stored_hash = self.auth.load_master_hash()
        if not stored_hash:
            messagebox.showwarning("No Account", "Please create an account first.")
            return

        if self.auth.verify_master_password(password, stored_hash):
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.root.destroy()
            self.on_login_success(username, password)
        else:
            messagebox.showerror("Failed", "Incorrect username or master password!")

    def set_master_password(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and Master Password are required!")
            return

        # Strong Password Validation
        if not self.is_strong_password(password):
            messagebox.showwarning("Weak Password", 
                "Your Master Password is too weak!\n\n"
                "It must contain:\n"
                "• At least 8 characters\n"
                "• At least 1 letter (A-Z)\n"
                "• At least 1 number (0-9)\n"
                "• At least 1 symbol (@, $, !, %, *, #, ?)")
            return

        # Save if strong
        hashed = self.auth.hash_master_password(password)
        self.auth.save_master_hash(hashed)

        with open("user_profile.txt", "w", encoding="utf-8") as f:
            f.write(username)

        messagebox.showinfo("Success", 
                          f"Strong Master Password Created!\n\n"
                          f"Account for '{username}' is ready.\n"
                          "Please login with your credentials.")

    def on_login_success(self, username: str, master_password: str):
        pass

    def run(self):
        self.root.mainloop()