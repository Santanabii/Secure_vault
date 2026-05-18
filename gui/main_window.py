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
    def __init__(self, username: str, master_password: str):
        self.username = username.lower()
        self.master_password = master_password
        self.encryption = EncryptionManager(master_password)
        self.db = DatabaseHandler()
        
        self.root = ctk.CTk()
        self.root.title(f"SecureVault - {username}")
        self.root.geometry("1350x780")
        
        self.setup_ui()
        self.refresh_password_list()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        sidebar = ctk.CTkFrame(self.root, width=260, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="SecureVault", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)

        ctk.CTkButton(sidebar, text="All Passwords", height=50, command=self.show_passwords).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Add New", height=50, command=self.add_new_password).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Password Generator", height=50, command=self.show_generator).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Dashboard", height=50, command=self.show_dashboard).pack(pady=8, padx=20, fill="x")

        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_passwords()

    def show_passwords(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10, padx=15)
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search...", width=500)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_password_list())

        columns = ("ID", "Site", "Username", "URL", "Category")
        self.tree = ttk.Treeview(self.main_content, columns=columns, show="headings", height=16)
        for col, w in zip(columns, [70, 220, 220, 300, 140]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree.bind("<Double-1>", self.open_url)

        btn_frame = ctk.CTkFrame(self.main_content)
        btn_frame.pack(pady=15, padx=15, fill="x")

        for text, cmd, color in [
            ("Show Password", self.show_password, None),
            ("Edit", self.edit_password, None),
            ("Copy Username", self.copy_username, None),
            ("Copy Password", self.copy_password, None),
            ("Delete", self.delete_password, None)
        ]:
            ctk.CTkButton(btn_frame, text=text, command=cmd, fg_color=color, height=42).pack(
                side="left", padx=6, fill="x", expand=True)

        self.refresh_password_list()

    def refresh_password_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.db.get_all_passwords(self.username):
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
                if not url.startswith(("http", "https")):
                    url = "https://" + url
                webbrowser.open(url)

    def show_password(self):
        selected = self.tree.selection()
        if not selected: 
            messagebox.showwarning("Select", "Please select a password")
            return
        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords(self.username):
            if str(entry["_id"])[-8:] == short_id:
                decrypted = self.encryption.decrypt(entry["password"])
                messagebox.showinfo("Password", f"Site: {entry['site']}\n\nPassword: {decrypted}")
                return

    def copy_password(self):
        selected = self.tree.selection()
        if not selected: 
            messagebox.showwarning("Select", "Please select a password")
            return
        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords(self.username):
            if str(entry["_id"])[-8:] == short_id:
                decrypted = self.encryption.decrypt(entry["password"])
                pyperclip.copy(decrypted)
                messagebox.showinfo("Copied", "Password copied!")
                return

    def edit_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password to edit")
            return
        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords(self.username):
            if str(entry["_id"])[-8:] == short_id:
                AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list, self.username, entry)
                return

    def delete_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password to delete")
            return
        if messagebox.askyesno("Confirm", "Delete this password permanently?"):
            short_id = self.tree.item(selected[0])['values'][0]
            for entry in self.db.get_all_passwords(self.username):
                if str(entry["_id"])[-8:] == short_id:
                    self.db.delete_password(entry["_id"], self.username)
                    messagebox.showinfo("Success", "Password deleted!")
                    self.refresh_password_list()
                    return

    def copy_username(self):
        selected = self.tree.selection()
        if selected:
            pyperclip.copy(self.tree.item(selected[0])['values'][2])
            messagebox.showinfo("Copied", "Username copied!")

    def add_new_password(self):
        AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list, self.username)

    def show_generator(self):
        gen_win = ctk.CTkToplevel(self.root)
        gen_win.title("Password Generator")
        gen_win.geometry("520x500")
        gen_win.grab_set()   # Make it modal

        ctk.CTkLabel(gen_win, text="Strong Password Generator", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Length Input
        ctk.CTkLabel(gen_win, text="Password Length", font=ctk.CTkFont(size=14)).pack(pady=(10,5))
        self.length_var = ctk.CTkEntry(gen_win, width=180, placeholder_text="16")
        self.length_var.pack(pady=5)
        self.length_var.insert(0, "16")

        # Options
        self.include_upper = ctk.CTkCheckBox(gen_win, text="Include Uppercase (A-Z)")
        self.include_upper.select()
        self.include_upper.pack(pady=8, anchor="w", padx=80)

        self.include_numbers = ctk.CTkCheckBox(gen_win, text="Include Numbers (0-9)")
        self.include_numbers.select()
        self.include_numbers.pack(pady=8, anchor="w", padx=80)

        self.include_symbols = ctk.CTkCheckBox(gen_win, text="Include Symbols (@$!%*&^)")
        self.include_symbols.select()
        self.include_symbols.pack(pady=8, anchor="w", padx=80)

        # Result
        ctk.CTkLabel(gen_win, text="Generated Password", font=ctk.CTkFont(size=14)).pack(pady=(20,5))
        self.result_entry = ctk.CTkEntry(gen_win, width=420, font=ctk.CTkFont(size=15))
        self.result_entry.pack(pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(gen_win)
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Generate", width=150, 
                     command=self.generate_password).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Copy", width=150, 
                     command=self.copy_generated_password).pack(side="left", padx=10)

    def generate_password(self):
        """Generate strong password"""
        try:
            length = int(self.length_var.get())
            if length < 6 or length > 64:
                length = 16
        except:
            length = 16

        characters = string.ascii_lowercase
        if self.include_upper.get():
            characters += string.ascii_uppercase
        if self.include_numbers.get():
            characters += string.digits
        if self.include_symbols.get():
            characters += "@$!%*#?&^_+-="

        password = ''.join(random.choice(characters) for _ in range(length))

        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, password)

    def copy_generated_password(self):
        """Copy generated password to clipboard"""
        password = self.result_entry.get().strip()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Success", "Password copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "Generate a password first")

    def show_dashboard(self):
        total = len(self.db.get_all_passwords(self.username))
        dash = ctk.CTkToplevel(self.root)
        dash.title("Dashboard")
        dash.geometry("500x400")
        ctk.CTkLabel(dash, text=f"Total Passwords: {total}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=50)

    def run(self):
        self.root.mainloop()