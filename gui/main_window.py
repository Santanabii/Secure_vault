# gui/main_window.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import webbrowser
import pyperclip
import random
import string
from database.db_handler import DatabaseHandler
from security.encryption import EncryptionManager
from gui.add_edit_window import AddEditWindow


class MainWindow:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.encryption = EncryptionManager(master_password)
        self.db = DatabaseHandler()
        
        self.root = ctk.CTk()
        self.root.title("SecureVault - Password Manager")
        self.root.geometry("1320x760")
        self.root.minsize(1200, 680)
        
        self.setup_ui()
        self.refresh_password_list()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ==================== Sidebar ====================
        sidebar = ctk.CTkFrame(self.root, width=260, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="SecureVault", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)

        ctk.CTkButton(sidebar, text="All Passwords", height=50, 
                     command=self.show_passwords).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Add New", height=50, fg_color="green", 
                     command=self.add_new_password).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Password Generator", height=50, 
                     command=self.show_generator).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Dashboard", height=50, 
                     command=self.show_dashboard).pack(pady=8, padx=20, fill="x")

        # ==================== Main Content ====================
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_passwords()

    def show_passwords(self):
        """Main Passwords View"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Search Bar
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10, padx=15)

        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, 
                                       placeholder_text="Search site, username or URL...", 
                                       width=500)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_password_list())

        # Treeview
        columns = ("ID", "Site", "Username", "URL", "Category")
        self.tree = ttk.Treeview(self.main_content, columns=columns, show="headings", height=16)
        
        widths = [70, 220, 220, 300, 140]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree.bind("<Double-1>", self.open_url)

        # Action Buttons (Clearly Visible)
        btn_frame = ctk.CTkFrame(self.main_content)
        btn_frame.pack(pady=15, padx=15, fill="x")

        buttons = [
            ("Show Password", self.show_password, "#1f8a1f"),
            ("Edit", self.edit_password, "orange"),
            ("Copy Username", self.copy_username, None),
            ("Copy Password", self.copy_password, None),
            ("Delete", self.delete_password, "red")
        ]

        for text, cmd, color in buttons:
            ctk.CTkButton(btn_frame, text=text, command=cmd, fg_color=color, height=42).pack(
                side="left", padx=6, fill="x", expand=True)

        self.refresh_password_list()

    def refresh_password_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in self.db.get_all_passwords():
            self.tree.insert("", "end", values=(
                str(p.get("_id"))[-8:],
                p.get("site", ""),
                p.get("username", ""),
                p.get("url", "No URL"),
                p.get("category", "Other")
            ))

    def open_url(self, event):
        selected = self.tree.selection()
        if selected:
            url = self.tree.item(selected[0])['values'][3]
            if url and url != "No URL":
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                webbrowser.open(url)

    # ====================== CORE FEATURES ======================
    def show_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password")
            return

        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords():
            if str(entry["_id"])[-8:] == short_id:
                try:
                    decrypted = self.encryption.decrypt(entry["password"])
                    messagebox.showinfo("Password", f"Site: {entry['site']}\n\nPassword: {decrypted}")
                except:
                    messagebox.showerror("Error", "Failed to decrypt password")
                return

    def copy_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password")
            return

        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords():
            if str(entry["_id"])[-8:] == short_id:
                try:
                    decrypted = self.encryption.decrypt(entry["password"])
                    pyperclip.copy(decrypted)
                    messagebox.showinfo("Copied", "Password copied to clipboard!")
                except:
                    messagebox.showerror("Error", "Failed to decrypt password")
                return

    def edit_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password to edit")
            return

        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords():
            if str(entry["_id"])[-8:] == short_id:
                AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list, entry)
                return

    def delete_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Delete this password permanently?\nThis action cannot be undone."):
            short_id = self.tree.item(selected[0])['values'][0]
            for entry in self.db.get_all_passwords():
                if str(entry["_id"])[-8:] == short_id:
                    if self.db.delete_password(entry["_id"]):
                        messagebox.showinfo("Success", "Password deleted successfully!")
                        self.refresh_password_list()
                        return

    def copy_username(self):
        selected = self.tree.selection()
        if selected:
            username = self.tree.item(selected[0])['values'][2]
            pyperclip.copy(username)
            messagebox.showinfo("Copied", "Username copied to clipboard!")

    def add_new_password(self):
        AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list)

    # ====================== EXTRA FEATURES ======================
    def show_generator(self):
        gen_win = ctk.CTkToplevel(self.root)
        gen_win.title("Password Generator")
        gen_win.geometry("500x450")
        gen_win.grab_set()

        ctk.CTkLabel(gen_win, text="Strong Password Generator", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        ctk.CTkLabel(gen_win, text="Password Length").pack(pady=(10,5))
        self.length_entry = ctk.CTkEntry(gen_win, width=150)
        self.length_entry.pack(pady=5)
        self.length_entry.insert(0, "16")

        self.include_symbols = ctk.CTkCheckBox(gen_win, text="Include Symbols (@$!%*&)")
        self.include_symbols.select()
        self.include_symbols.pack(pady=8)

        self.result_entry = ctk.CTkEntry(gen_win, width=400, font=ctk.CTkFont(size=14))
        self.result_entry.pack(pady=20)

        ctk.CTkButton(gen_win, text="Generate", command=self.generate_password).pack(pady=5)
        ctk.CTkButton(gen_win, text="Copy", command=self.copy_generated).pack(pady=5)

    def generate_password(self):
        try:
            length = int(self.length_entry.get())
        except:
            length = 16
        chars = string.ascii_letters + string.digits
        if self.include_symbols.get():
            chars += "@$!%*#?&^_+-="
        pwd = ''.join(random.choice(chars) for _ in range(length))
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, pwd)

    def copy_generated(self):
        pwd = self.result_entry.get()
        if pwd:
            pyperclip.copy(pwd)
            messagebox.showinfo("Copied", "Password copied!")

    def show_dashboard(self):
        total = len(self.db.get_all_passwords())
        dash = ctk.CTkToplevel(self.root)
        dash.title("Dashboard")
        dash.geometry("600x500")
        ctk.CTkLabel(dash, text=f"Total Passwords: {total}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=40)

    def run(self):
        self.root.mainloop()