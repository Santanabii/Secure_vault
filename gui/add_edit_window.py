# gui/add_edit_window.py
import customtkinter as ctk
from tkinter import messagebox
import re
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
        self.window.geometry("560x780")
        self.window.grab_set()

        self.setup_ui()

    def setup_ui(self):
        title = "Edit Password" if self.entry_to_edit else "Add New Password"
        ctk.CTkLabel(self.window, text=title, font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # Site
        ctk.CTkLabel(self.window, text="Website / App Name *").pack(anchor="w", padx=50, pady=(10,2))
        self.site_entry = ctk.CTkEntry(self.window, width=450, height=40)
        self.site_entry.pack(pady=5, padx=50)

        # Username
        ctk.CTkLabel(self.window, text="Username / Email *").pack(anchor="w", padx=50, pady=(10,2))
        self.username_entry = ctk.CTkEntry(self.window, width=450, height=40)
        self.username_entry.pack(pady=5, padx=50)

        # URL
        ctk.CTkLabel(self.window, text="URL / Link (Optional)").pack(anchor="w", padx=50, pady=(10,2))
        self.url_entry = ctk.CTkEntry(self.window, width=450, height=40, placeholder_text="https://example.com")
        self.url_entry.pack(pady=5, padx=50)

        # Password with Strength
        ctk.CTkLabel(self.window, text="Password *").pack(anchor="w", padx=50, pady=(15,2))
        self.password_entry = ctk.CTkEntry(self.window, width=450, height=40, show="*")
        self.password_entry.pack(pady=5, padx=50)
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)

        # Strength Indicator
        self.strength_label = ctk.CTkLabel(self.window, text="Password Strength: -", font=ctk.CTkFont(size=14))
        self.strength_label.pack(pady=5)

        # Category
        ctk.CTkLabel(self.window, text="Category").pack(anchor="w", padx=50, pady=(10,2))
        self.category_entry = ctk.CTkEntry(self.window, width=450, height=40, placeholder_text="Social, Banking, Work...")
        self.category_entry.pack(pady=5, padx=50)

        # Save Button
        btn_text = "Update Password" if self.entry_to_edit else "Save Password"
        ctk.CTkButton(self.window, text=btn_text, height=50, font=ctk.CTkFont(size=16, weight="bold"),
                     command=self.save_password).pack(pady=30)

        if self.entry_to_edit:
            self.pre_fill_data()

    def check_password_strength(self, event=None):
        """Real-time password strength checker"""
        password = self.password_entry.get()

        if len(password) == 0:
            self.strength_label.configure(text="Password Strength: -", text_color="gray")
            return

        score = 0
        feedback = []

        if len(password) >= 8:
            score += 1
        else:
            feedback.append("At least 8 characters")

        if re.search(r"[A-Z]", password):
            score += 1
        else:
            feedback.append("Uppercase letter")

        if re.search(r"[a-z]", password):
            score += 1

        if re.search(r"[0-9]", password):
            score += 1
        else:
            feedback.append("Number")

        if re.search(r"[@$!%*#?&^_+=]", password):
            score += 1
        else:
            feedback.append("Symbol")

        # Set color and text
        if score >= 5:
            strength = "Strong"
            color = "green"
        elif score >= 3:
            strength = "Medium"
            color = "orange"
        else:
            strength = "Weak"
            color = "red"

        self.strength_label.configure(
            text=f"Password Strength: {strength}",
            text_color=color
        )

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

        # Final strength check
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[0-9]", password):
            messagebox.showwarning("Weak Password", "Password is too weak!\nUse uppercase, numbers and symbols.")
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
                self.db.update_password(self.entry_to_edit["_id"], data, self.username)
                messagebox.showinfo("Success", "Password updated successfully!")
            else:
                self.db.insert_password(data, self.username)
                messagebox.showinfo("Success", "Password saved successfully!")

            self.refresh_callback()
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save password:\n{str(e)}")