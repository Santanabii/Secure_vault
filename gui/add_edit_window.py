# gui/add_edit_window.py
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

class AddEditWindow:
    def __init__(self, parent, encryption, db_handler, refresh_callback, username: str, entry_to_edit=None):
        self.encryption = encryption
        self.db = db_handler
        self.refresh_callback = refresh_callback
        self.username = username.lower()
        self.entry_to_edit = entry_to_edit

        self.window = ctk.CTkToplevel(parent)
        self.window.title("Edit Password" if entry_to_edit else "Add New Password")
        self.window.geometry("550x750")
        self.window.grab_set()
        self.window.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        title = "Edit Password" if self.entry_to_edit else "Add New Password"
        ctk.CTkLabel(self.window, text=title, font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # Site
        ctk.CTkLabel(self.window, text="Website / App Name *").pack(anchor="w", padx=50, pady=(10,2))
        self.site_entry = ctk.CTkEntry(self.window, width=440, height=40)
        self.site_entry.pack(pady=5, padx=50)

        # Username
        ctk.CTkLabel(self.window, text="Username / Email *").pack(anchor="w", padx=50, pady=(10,2))
        self.username_entry = ctk.CTkEntry(self.window, width=440, height=40)
        self.username_entry.pack(pady=5, padx=50)

        # URL
        ctk.CTkLabel(self.window, text="URL / Link (Optional)").pack(anchor="w", padx=50, pady=(10,2))
        self.url_entry = ctk.CTkEntry(self.window, width=440, height=40, placeholder_text="https://example.com")
        self.url_entry.pack(pady=5, padx=50)

        # Password
        ctk.CTkLabel(self.window, text="Password *").pack(anchor="w", padx=50, pady=(10,2))
        self.password_entry = ctk.CTkEntry(self.window, width=440, height=40, show="*")
        self.password_entry.pack(pady=5, padx=50)

        # Category
        ctk.CTkLabel(self.window, text="Category").pack(anchor="w", padx=50, pady=(10,2))
        self.category_entry = ctk.CTkEntry(self.window, width=440, height=40, placeholder_text="Social, Banking, Work...")
        self.category_entry.pack(pady=5, padx=50)

        # Save Button
        btn_text = "Update Password" if self.entry_to_edit else "Save Password"
        ctk.CTkButton(self.window, text=btn_text, height=50, font=ctk.CTkFont(size=16, weight="bold"),
                     command=self.save_password).pack(pady=30)

        if self.entry_to_edit:
            self.pre_fill_data()

    def pre_fill_data(self):
        self.site_entry.insert(0, self.entry_to_edit.get("site", ""))
        self.username_entry.insert(0, self.entry_to_edit.get("username", ""))
        self.url_entry.insert(0, self.entry_to_edit.get("url", ""))
        self.category_entry.insert(0, self.entry_to_edit.get("category", ""))

    def save_password(self):
        site = self.site_entry.get().strip()
        user_field = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        url = self.url_entry.get().strip()
        category = self.category_entry.get().strip()

        if not site or not user_field or not password:
            messagebox.showerror("Error", "Site, Username and Password are required!")
            return

        try:
            encrypted_pass = self.encryption.encrypt(password)

            data = {
                "site": site,
                "username": user_field,
                "password": encrypted_pass,
                "url": url,
                "category": category or "Other"
            }

            if self.entry_to_edit:
                success = self.db.update_password(self.entry_to_edit["_id"], data, self.username)
                messagebox.showinfo("Success", "Password updated successfully!")
            else:
                self.db.insert_password(data, self.username)
                messagebox.showinfo("Success", "Password saved successfully!")

            self.refresh_callback()
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{str(e)}")