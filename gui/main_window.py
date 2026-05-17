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
        
        self.root = ctk.CTk()
        self.root.title("SecureVault - Password Manager")
        self.root.geometry("1280x720")
        
        self.setup_ui()
        self.refresh_password_list()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sidebar
        sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
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

    # ==================== Password List ====================
    def show_passwords(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Search
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10, padx=15)
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search...", width=500)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_password_list())

        # Treeview
        columns = ("ID", "Site", "Username", "URL", "Category")
        self.tree = ttk.Treeview(self.main_content, columns=columns, show="headings")
        for col, width in zip(columns, [70, 220, 220, 300, 140]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        self.tree.bind("<Double-1>", self.open_url)

        # Buttons
        btn_frame = ctk.CTkFrame(self.main_content)
        btn_frame.pack(pady=12)
        for text, cmd, color in [
            ("View", self.view_password, None),
            ("Edit", self.edit_password, "orange"),
            ("Copy User", self.copy_username, None),
            ("Copy Pass", self.copy_password, None),
            ("Delete", self.delete_password, "red")
        ]:
            ctk.CTkButton(btn_frame, text=text, command=cmd, fg_color=color).pack(side="left", padx=5)

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
                if not url.startswith("http"):
                    url = "https://" + url
                webbrowser.open(url)

    # ==================== CRUD ====================
    def add_new_password(self):
        AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list)

    def edit_password(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a record")
            return
        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords():
            if str(entry["_id"])[-8:] == short_id:
                AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list, entry)
                return

    def delete_password(self):
        selected = self.tree.selection()
        if not selected or not messagebox.askyesno("Confirm", "Delete this password?"):
            return
        short_id = self.tree.item(selected[0])['values'][0]
        for entry in self.db.get_all_passwords():
            if str(entry["_id"])[-8:] == short_id:
                self.db.delete_password(entry["_id"])
                messagebox.showinfo("Success", "Password deleted")
                self.refresh_password_list()
                return

    def copy_username(self):
        selected = self.tree.selection()
        if selected:
            pyperclip.copy(self.tree.item(selected[0])['values'][2])
            messagebox.showinfo("Copied", "Username copied!")

    def copy_password(self):
        messagebox.showinfo("Info", "Copy password coming soon")

    def view_password(self):
        messagebox.showinfo("Info", "View password feature coming soon")

    # ==================== Password Generator ====================
    def show_generator(self):
        gen_win = ctk.CTkToplevel(self.root)
        gen_win.title("Password Generator")
        gen_win.geometry("500x400")

        length_var = ctk.IntVar(value=16)
        ctk.CTkLabel(gen_win, text="Password Length", font=ctk.CTkFont(size=16)).pack(pady=10)
        ctk.CTkSlider(gen_win, from_=8, to=32, variable=length_var, number_of_steps=24).pack(pady=10)

        result = ctk.CTkEntry(gen_win, width=400)
        result.pack(pady=20)

        def generate():
            length = length_var.get()
            chars = string.ascii_letters + string.digits + "@$!%*#?&"
            pwd = ''.join(random.choice(chars) for _ in range(length))
            result.delete(0, "end")
            result.insert(0, pwd)

        ctk.CTkButton(gen_win, text="Generate Strong Password", command=generate).pack(pady=10)
        ctk.CTkButton(gen_win, text="Copy", command=lambda: pyperclip.copy(result.get())).pack(pady=5)

    # ==================== Dashboard ====================
    def show_dashboard(self):
        dash = ctk.CTkToplevel(self.root)
        dash.title("Dashboard")
        dash.geometry("600x500")
        total = len(self.db.get_all_passwords())
        ctk.CTkLabel(dash, text=f"Total Passwords: {total}", font=ctk.CTkFont(size=20)).pack(pady=30)
        ctk.CTkLabel(dash, text="More statistics coming soon...", font=ctk.CTkFont(size=14)).pack(pady=20)

    def run(self):
        self.root.mainloop()