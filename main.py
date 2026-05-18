# main.py
from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    login_window = LoginWindow()
    
    def on_successful_login(username: str, master_password: str):
        print(f" Login Successful! Welcome, {username}")
        app = MainWindow(username=username, master_password=master_password)
        app.run()
    
    login_window.on_login_success = on_successful_login
    login_window.run()


if __name__ == "__main__":
    main()