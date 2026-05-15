# gui/main_window.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import webbrowser
from database.db_handler import DatabaseHandler
from security.encryption import EncryptionManager
from gui.add_edit_window import AddEditWindow
import pyperclip


class MainWindow:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.encryption = EncryptionManager(master_password)
        self.db = DatabaseHandler()
        
        self.root = ctk.CTk()
        self.root.title("SecureVault - Password Manager")
        self.root.geometry("1200x720")
        
        self.setup_ui()
        self.refresh_password_list()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sidebar
        sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="SecureVault", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=25)

        ctk.CTkButton(sidebar, text="All Passwords", height=45, command=self.show_passwords).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Add New", height=45, fg_color="green", command=self.add_new_password).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Password Generator", height=45, command=self.show_generator).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Dashboard", height=45, command=self.show_dashboard).pack(pady=8, padx=20, fill="x")

        # Main Content
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_passwords()

    def show_passwords(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Search
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search site, username or URL", width=500)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_password_list())

        # Treeview with URL Column
        columns = ("ID", "Site", "Username", "URL", "Category")
        self.tree = ttk.Treeview(self.main_content, columns=columns, show="headings", height=18)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Site", text="Website / App")
        self.tree.heading("Username", text="Username")
        self.tree.heading("URL", text="URL / Link")
        self.tree.heading("Category", text="Category")

        # Column Widths
        self.tree.column("ID", width=60)
        self.tree.column("Site", width=220)
        self.tree.column("Username", width=220)
        self.tree.column("URL", width=280)
        self.tree.column("Category", width=140)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Double-click to open URL
        self.tree.bind("<Double-1>", self.on_double_click)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self.main_content)
        btn_frame.pack(pady=12)

        ctk.CTkButton(btn_frame, text="View Password", command=self.view_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy Username", command=self.copy_username).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy Password", command=self.copy_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", fg_color="red", command=self.delete_password).pack(side="left", padx=5)

        self.refresh_password_list()

    def refresh_password_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_entry.get().strip() if hasattr(self, 'search_entry') else ""

        passwords = self.db.get_all_passwords()
        
        for p in passwords:
            self.tree.insert("", "end", values=(
                str(p.get("_id"))[-8:],           # Short ID
                p.get("site", ""),
                p.get("username", ""),
                p.get("url", "No Link"),          # New URL field
                p.get("category", "Other")
            ))

    def on_double_click(self, event):
        """Open URL when user double-clicks on a row"""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        url = values[3]  # URL is in column index 3

        if url and url != "No Link":
            if not url.startswith("http"):
                url = "https://" + url
            try:
                webbrowser.open(url)
            except Exception:
                messagebox.showerror("Error", "Could not open link")
        else:
            messagebox.showinfo("No Link", "No URL saved for this entry")

    # ==================== Other Methods ====================
    def add_new_password(self):
        AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list)

    def view_password(self):
        messagebox.showinfo("Coming Soon", "Full 'View Password' feature in next update")

    def copy_username(self):
        selected = self.tree.selection()
        if selected:
            username = self.tree.item(selected[0])['values'][2]
            pyperclip.copy(username)
            messagebox.showinfo("Copied", "Username copied!")

    def copy_password(self):
        messagebox.showinfo("Info", "Copy Password feature coming soon")

    def delete_password(self):
        messagebox.showinfo("Info", "Delete feature coming in Day 4")

    def show_generator(self):
        messagebox.showinfo("Generator", "Password Generator coming soon")

    def show_dashboard(self):
        messagebox.showinfo("Dashboard", "Dashboard coming soon")

    def run(self):
        self.root.mainloop()