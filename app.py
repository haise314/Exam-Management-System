import customtkinter as ctk
import sqlite3
from datetime import datetime
import os
import sys

# Import other modules we'll create
from database_manager import DatabaseManager
from admin_dashboard import AdminDashboard
from trainee_dashboard import TraineeDashboard
from exam_manager import ExamManager

class ExamManagementApp:
    def __init__(self):
        # Configure CustomTkinter
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Exam Management System")
        self.root.geometry("800x600")

        # Initialize database
        self.db_manager = DatabaseManager()

        # Create login frame
        self.create_login_frame()

    def create_login_frame(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Login Frame
        self.login_frame = ctk.CTkFrame(self.root)
        self.login_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            self.login_frame, 
            text="Exam Management System", 
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(40, 20))

        # Login Type Selection
        self.login_type = ctk.CTkSegmentedButton(
            self.login_frame, 
            values=["Admin", "Trainee"],
            command=self.toggle_login_mode
        )
        self.login_type.pack(pady=20)
        # self.login_type.set("Admin")

        # Username Entry
        self.username_label = ctk.CTkLabel(self.login_frame, text="Username")
        self.username_label.pack(pady=(10, 5))
        self.username_entry = ctk.CTkEntry(self.login_frame, width=300)
        self.username_entry.pack()

        # Password Entry (for admin)
        self.password_label = ctk.CTkLabel(self.login_frame, text="Password")
        self.password_label.pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", width=300)
        self.password_entry.pack()

        # Login Button
        login_button = ctk.CTkButton(
            self.login_frame, 
            text="Login", 
            command=self.login,
            width=300
        )
        login_button.pack(pady=20)

    def toggle_login_mode(self, mode):
        if mode == "Trainee":
            # Hide password for trainee
            self.password_label.pack_forget()
            self.password_entry.pack_forget()
        else:
            # Show password for admin
            self.password_label.pack(pady=(10, 5))
            self.password_entry.pack()

    def login(self):
        username = self.username_entry.get()
        login_type = self.login_type.get()

        if login_type == "Admin":
            # Validate admin login (you'd typically have a more secure method)
            password = self.password_entry.get()
            if username == "admin" and password == "admin123":
                self.open_admin_dashboard()
            else:
                self.show_error("Invalid admin credentials")
        else:
            # Trainee login (validate against database)
            if self.validate_trainee_login(username):
                self.open_trainee_dashboard(username)
            else:
                self.show_error("Invalid trainee credentials")

    def validate_trainee_login(self, username):
        # Connect to database and check if trainee exists
        conn = sqlite3.connect('exam_management.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trainees WHERE id_no = ?", (username,))
        trainee = cursor.fetchone()
        
        conn.close()
        return trainee is not None

    def open_admin_dashboard(self):
        # Clear login frame
        self.login_frame.destroy()
        
        # Open admin dashboard
        admin_dashboard = AdminDashboard(self.root, self.db_manager, self.return_to_login)

    def open_trainee_dashboard(self, username):
        # Clear login frame
        self.login_frame.destroy()
        
        # Open trainee dashboard
        trainee_dashboard = TraineeDashboard(
            self.root, 
            self.db_manager, 
            username, 
            self.return_to_login
        )

    def return_to_login(self):
        # Recreate login frame after logout
        self.create_login_frame()

    def show_error(self, message):
        # Create an error popup
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("Error")
        error_window.geometry("300x150")
        
        error_label = ctk.CTkLabel(
            error_window, 
            text=message, 
            text_color="red",
            wraplength=250
        )
        error_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        close_button = ctk.CTkButton(
            error_window, 
            text="Close", 
            command=error_window.destroy
        )
        close_button.pack(pady=10)

    def run(self):
        self.root.mainloop()

    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = ExamManagementApp()
    app.run()