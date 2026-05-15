# gui/add_edit_window.py
import customtkinter as ctk
from tkinter import messagebox

class AddEditWindow:
    def __init__(self, parent, encryption, db_handler, refresh_callback):
        self.encryption = encryption
        self.db = db_handler
        self.refresh_callback = refresh_callback
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Add New Password")
        self.window.geometry("500x600")
        self.window.grab_set()  # Make it modal
        
        self.setup_form()
    
    def setup_form(self):
        ctk.CTkLabel(self.window, text="Add New Entry", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        self.site_entry = ctk.CTkEntry(self.window, placeholder_text="Website / App Name", width=400)
        self.site_entry.pack(pady=10)
        
        self.username_entry = ctk.CTkEntry(self.window, placeholder_text="Username or Email", width=400)
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self.window, placeholder_text="Password", show="*", width=400)
        self.password_entry.pack(pady=10)
        
        self.category_entry = ctk.CTkEntry(self.window, placeholder_text="Category (e.g. Social, Banking)", width=400)
        self.category_entry.pack(pady=10)
        
        ctk.CTkButton(self.window, text="Save Password", height=40, command=self.save_password).pack(pady=30)
    
    def save_password(self):
        site = self.site_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        category = self.category_entry.get().strip()
        
        if not site or not username or not password:
            messagebox.showerror("Error", "Site, Username, and Password are required!")
            return
        
        try:
            encrypted_pass = self.encryption.encrypt(password)
            
            data = {
                "site": site,
                "username": username,
                "password": encrypted_pass,
                "category": category or "Other"
            }
            
            self.db.insert_password(data)
            messagebox.showinfo("Success", "Password saved successfully!")
            self.refresh_callback()
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")