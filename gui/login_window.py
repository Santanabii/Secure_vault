# gui/login_window.py
import customtkinter as ctk
from tkinter import messagebox
from security.auth import AuthManager
from config import APP_NAME, MASTER_PASSWORD_MIN_LENGTH


class LoginWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} - Login")
        self.root.geometry("420x380")
        self.root.resizable(False, False)
        
        self.auth = AuthManager()
        self.setup_ui()

    def setup_ui(self):
        """Setup the login window UI"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Title
        title_label = ctk.CTkLabel(self.root, 
                                  text=APP_NAME, 
                                  font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=30)

        subtitle = ctk.CTkLabel(self.root, 
                               text="Secure Password Manager", 
                               font=ctk.CTkFont(size=14))
        subtitle.pack(pady=(0, 20))

        # Password Entry
        self.password_entry = ctk.CTkEntry(self.root, 
                                         placeholder_text="Enter Master Password",
                                         show="*", 
                                         width=300, 
                                         height=45,
                                         font=ctk.CTkFont(size=14))
        self.password_entry.pack(pady=15)
        self.password_entry.focus()

        # Login Button
        login_btn = ctk.CTkButton(self.root, 
                                 text="Login", 
                                 width=300, 
                                 height=45,
                                 font=ctk.CTkFont(size=16),
                                 command=self.login)
        login_btn.pack(pady=10)

        # Set Master Password Button
        setup_btn = ctk.CTkButton(self.root, 
                                 text="First Time? Set Master Password",
                                 width=300, 
                                 height=40,
                                 fg_color="transparent", 
                                 border_width=2,
                                 command=self.set_master_password)
        setup_btn.pack(pady=10)

        # Footer
        footer = ctk.CTkLabel(self.root, 
                             text="Your passwords are encrypted locally", 
                             font=ctk.CTkFont(size=12),
                             text_color="gray")
        footer.pack(pady=20)

    def login(self):
        """Handle login"""
        password = self.password_entry.get().strip()

        if not password:
            messagebox.showwarning("Input Error", "Please enter your master password")
            return

        stored_hash = self.auth.load_master_hash()

        if not stored_hash:
            messagebox.showwarning("Setup Required", 
                                 "No master password found.\nPlease set one first.")
            return

        if self.auth.verify_master_password(password, stored_hash):
            messagebox.showinfo("Success", "Login Successful! ✅")
            self.root.destroy()
            self.on_login_success(password)   # This calls main window
        else:
            messagebox.showerror("Login Failed", "Incorrect Master Password!")

    def set_master_password(self):
        """Set new master password"""
        password = self.password_entry.get().strip()

        if len(password) < MASTER_PASSWORD_MIN_LENGTH:
            messagebox.showerror("Error", 
                               f"Master password must be at least {MASTER_PASSWORD_MIN_LENGTH} characters long!")
            return

        hashed = self.auth.hash_master_password(password)
        self.auth.save_master_hash(hashed)
        
        messagebox.showinfo("Success", 
                          "Master Password Set Successfully!\n\nYou can now login.")

    def on_login_success(self, master_password):
        """This function will be replaced by main.py to open main window"""
        pass

    def run(self):
        """Start the login window"""
        self.root.mainloop()