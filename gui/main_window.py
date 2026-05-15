# gui/main_window.py
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
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
        self.root.geometry(f"{1000}x{650}")
        self.root.minsize(900, 600)
        
        self.setup_ui()
        self.load_passwords()
    
    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        title = ctk.CTkLabel(self.sidebar, text="SecureVault", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        ctk.CTkButton(self.sidebar, text="Dashboard", height=40, command=self.show_dashboard).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="All Passwords", height=40, command=self.show_passwords).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Add New", height=40, command=self.add_new_password).pack(pady=5, padx=20, fill="x")
        
        
        # Main Content Area
        self.main_content = ctk.CTkFrame(self.root)
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Default view - Password List
        self.show_passwords()
    
    def load_passwords(self):
        # Will be used by password list frame
        pass
    
    def show_passwords(self):
        # Clear main content
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        label = ctk.CTkLabel(self.main_content, text="All Passwords", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=10)
        
        # Search Bar
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by site or username", width=400)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_password_list())


        
        # Treeview will be added in next step
        self.tree = ttk.Treeview(self.main_content, columns=("site", "username", "category"), show="headings")
        self.tree.heading("site", text="Website / App")
        self.tree.heading("username", text="Username")
        self.tree.heading("category", text="Category")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load data
        self.refresh_password_list()
    
    def refresh_password_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        passwords = self.db.get_all_passwords()
        for p in passwords:
            self.tree.insert("", "end", values=(p.get("site"), p.get("username"), p.get("category", "Other")))
    
    def add_new_password(self):
        AddEditWindow(self.root, self.encryption, self.db, self.refresh_password_list)
    
    def show_dashboard(self):
        messagebox.showinfo("Dashboard")
    
    def show_generator(self):
        messagebox.showinfo("PasswordGenerator")
    
    def run(self):
        self.root.mainloop()