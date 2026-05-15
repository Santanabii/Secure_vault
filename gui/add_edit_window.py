# gui/main_window.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import webbrowser
import pyperclip
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
        self.root.geometry("1250x720")
        self.root.minsize(1100, 650)
        
        self.setup_ui()
        self.refresh_password_list()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sidebar
        sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="SecureVault", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=30)

        ctk.CTkButton(sidebar, text="All Passwords", height=45, 
                     command=self.show_passwords).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Add New", height=45, fg_color="green", 
                     command=self.add_new_password).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Password Generator", height=45, 
                     command=self.show_generator).pack(pady=8, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Dashboard", height=45, 
                     command=self.show_dashboard).pack(pady=8, padx=20, fill="x")

        # Main Content Area
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_passwords()

    def show_passwords(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Search Bar
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10, padx=15)

        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, 
                                       placeholder_text="Search by site, username or URL...", 
                                       width=500)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_password_list())

        # Treeview
        columns = ("ID", "Site", "Username", "URL", "Category")
        self.tree = ttk.Treeview(self.main_content, columns=columns, show="headings", height=18)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Site", text="Website / App")
        self.tree.heading("Username", text="Username")
        self.tree.heading("URL", text="URL")
        self.tree.heading("Category", text="Category")

        self.tree.column("ID", width=70)
        self.tree.column("Site", width=220)
        self.tree.column("Username", width=220)
        self.tree.column("URL", width=300)
        self.tree.column("Category", width=140)

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        # Double-click to open URL
        self.tree.bind("<Double-1>", self.open_url)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self.main_content)
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="View Password", command=self.view_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Edit", fg_color="orange", command=self.edit_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy Username", command=self.copy_username).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy Password", command=self.copy_password).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete", fg_color="red", command=self.delete_password).pack(side="left", padx=5)

        self.refresh_password_list()

    def refresh_password_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        passwords = self.db.get_all_passwords()

        for p in passwords:
            self.tree.insert("", "end", values=(
                str(p.get("_id"))[-8:],           # Short ID
                p.get("site", ""),
                p.get("username", ""),
                p.get("url", "No URL"),
                p.get("category", "Other")
            ))

    def open_url(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        url = self.tree.item(selected[0])['values'][3]
        if url and url != "No URL":
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)

    # ====================== CRUD Operations ======================

    def add_new_password(self):
        AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list)

    def edit_password(self):
        """Edit selected password"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a password to edit")
            return

        short_id = self.tree.item(selected[0])['values'][0]

        try:
            all_passwords = self.db.get_all_passwords()
            entry_to_edit = None
            for entry in all_passwords:
                if str(entry.get("_id"))[-8:] == short_id:
                    entry_to_edit = entry
                    break

            if entry_to_edit:
                AddEditWindow(
                    parent=self.root,
                    encryption=self.encryption,
                    db_handler=self.db,
                    refresh_callback=self.refresh_password_list,
                    entry_to_edit=entry_to_edit
                )
            else:
                messagebox.showerror("Error", "Could not find the selected password.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load password:\n{str(e)}")

    def delete_password(self):
        """Delete selected password"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a password to delete")
            return

        if messagebox.askyesno("Confirm Delete", 
                             "Are you sure you want to permanently delete this password?\n"
                             "This action cannot be undone!"):
            try:
                short_id = self.tree.item(selected[0])['values'][0]
                all_passwords = self.db.get_all_passwords()

                for entry in all_passwords:
                    if str(entry.get("_id"))[-8:] == short_id:
                        self.db.delete_password(entry["_id"])
                        messagebox.showinfo("Success", "Password deleted successfully!")
                        self.refresh_password_list()
                        return

                messagebox.showerror("Error", "Could not delete password.")
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed:\n{str(e)}")

    def view_password(self):
        messagebox.showinfo("View Password", "Full View/Show Password feature coming soon.")

    def copy_username(self):
        selected = self.tree.selection()
        if selected:
            username = self.tree.item(selected[0])['values'][2]
            pyperclip.copy(username)
            messagebox.showinfo("Copied", "Username copied to clipboard!")

    def copy_password(self):
        messagebox.showinfo("Coming Soon", "Copy Password feature will be added soon.")

    def show_generator(self):
        messagebox.showinfo("Password Generator", "Strong Password Generator coming soon.")

    def show_dashboard(self):
        messagebox.showinfo("Dashboard", "Statistics Dashboard coming in final update.")

    def run(self):
        self.root.mainloop()