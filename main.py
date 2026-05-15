# main.py
import customtkinter as ctk
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    # Create login window
    login_window = LoginWindow()
    
    # This function will be called after successful login
    def on_successful_login(username: str ,master_password: str):
        print(" Login Successful! Opening Main Application...")
        
        # Close login window and open main application
        try:
            app = MainWindow(master_password)
            app.run()
        except Exception as e:
            print("Error opening main window:", e)
    
    # Connect the callback
    login_window.on_login_success = on_successful_login
    
    # Start the login window
    login_window.run()


if __name__ == "__main__":
    main()