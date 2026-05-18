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
from bson import ObjectId


class MainWindow:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.encryption = EncryptionManager(master_password)
        self.db = DatabaseHandler()
        self.current_view_password = None  # For show/hide
        
        self.root = ctk.CTk()
        self.root.title("SecureVault - Password Manager")
        self.root.geometry("1300x740")
        
        self.setup_ui()
        self.refresh_password_list()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sidebar
        sidebar = ctk.CTkFrame(self.root, width=260, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="SecureVault", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=30)

        ctk.CTkButton(sidebar, text="All Passwords", height=50, command=self.show_passwords).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Add New", height=50, fg_color="green", command=self.add_new_password).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Password Generator", height=50, command=self.show_generator).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Dashboard", height=50, command=self.show_dashboard).pack(pady=8, padx=20, fill="x")

        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_passwords()

    def show_passwords(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Search
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10, padx=15)
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search site, username...", width=500)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_password_list())

        # Treeview
        columns = ("ID", "Site", "Username", "URL", "Category")
        self.tree = ttk.Treeview(self.main_content, columns=columns, show="headings", height=18)
        
        for col, w in zip(columns, [70, 220, 220, 300, 140]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.tree.bind("<Double-1>", self.open_url)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self.main_content)
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Show Password", fg_color="#1f8a1f", command=self.show_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Edit", fg_color="orange", command=self.edit_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy Username", command=self.copy_username).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy Password", command=self.copy_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", fg_color="red", command=self.delete_password).pack(side="left", padx=5)

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
                if not url.startswith(("http", "https")):
                    url = "https://" + url
                webbrowser.open(url)

    # ====================== VIEW PASSWORD (Show/Hide) ======================
    def show_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password")
            return

        short_id = self.tree.item(selected[0])['values'][0]

        try:
            for entry in self.db.get_all_passwords():
                if str(entry["_id"])[-8:] == short_id:
                    decrypted = self.encryption.decrypt(entry["password"])
                    messagebox.showinfo("Password", f"Password for {entry['site']}:\n\n{decrypted}")
                    return
        except Exception as e:
            messagebox.showerror("Error", f"Could not decrypt password: {e}")

    # ====================== COPY PASSWORD ======================
    def copy_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a password")
            return

        short_id = self.tree.item(selected[0])['values'][0]

        try:
            for entry in self.db.get_all_passwords():
                if str(entry["_id"])[-8:] == short_id:
                    decrypted = self.encryption.decrypt(entry["password"])
                    pyperclip.copy(decrypted)
                    messagebox.showinfo("Copied", "Password copied to clipboard!")
                    return
        except Exception as e:
            messagebox.showerror("Error", "Failed to copy password")

    # ====================== EDIT ======================
    def edit_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a record to edit")
            return

        short_id = self.tree.item(selected[0])['values'][0]

        for entry in self.db.get_all_passwords():
            if str(entry["_id"])[-8:] == short_id:
                AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list, entry)
                return

    # ====================== DELETE ======================
    def delete_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a record to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Delete this password permanently?\nThis cannot be undone!"):
            short_id = self.tree.item(selected[0])['values'][0]

            for entry in self.db.get_all_passwords():
                if str(entry["_id"])[-8:] == short_id:
                    if self.db.delete_password(entry["_id"]):
                        messagebox.showinfo("Success", "Password deleted successfully!")
                        self.refresh_password_list()
                        return
            messagebox.showerror("Error", "Failed to delete password")

    # ====================== Other Functions ======================
    def add_new_password(self):
        AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list)

    def copy_username(self):
        selected = self.tree.selection()
        if selected:
            pyperclip.copy(self.tree.item(selected[0])['values'][2])
            messagebox.showinfo("Copied", "Username copied!")

    def show_generator(self):
        # (Use the improved generator I gave you earlier)
        pass   # Paste the improved generator here if needed

    def show_dashboard(self):
        total = len(self.db.get_all_passwords())
        dash = ctk.CTkToplevel(self.root)
        dash.title("Dashboard")
        dash.geometry("500x400")
        ctk.CTkLabel(dash, text=f"Total Passwords Stored: {total}", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=40)

    def run(self):
        self.root.mainloop()