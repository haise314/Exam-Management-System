import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class TraineeDashboard:
    def __init__(self, master, db_manager, username, logout_callback):
        self.master = master
        self.db_manager = db_manager
        self.username = username
        self.logout_callback = logout_callback

        # Create main trainee dashboard frame
        self.trainee_frame = ctk.CTkFrame(master)
        self.trainee_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Fetch trainee details
        trainee_details = self.get_trainee_details()

        # Create dashboard title
        title_label = ctk.CTkLabel(
            self.trainee_frame, 
            text=f"Trainee Dashboard - {trainee_details['name']}", 
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(20, 10))

        # Create tabs
        self.tabview = ctk.CTkTabview(self.trainee_frame)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        # Add tabs
        tabs = ["Profile", "Exams", "Results"]
        for tab_name in tabs:
            tab = self.tabview.add(tab_name)
            self.create_tab_content(tab, tab_name.lower(), trainee_details)

        # Logout button
        logout_button = ctk.CTkButton(
            self.trainee_frame, 
            text="Logout", 
            command=self.logout
        )
        logout_button.pack(pady=10)

    def get_trainee_details(self):
        # Fetch trainee details from database
        conn = sqlite3.connect('exam_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM trainees 
            WHERE id_no = ?
        """, (self.username,))
        
        trainee = cursor.fetchone()
        
        conn.close()

        # Convert to dictionary for easy access
        columns = [
            'id', 'name', 'id_no', 'uli', 'batch_year', 
            'trainer_name', 'exams_taken', 'status', 'remarks', 'batch_id'
        ]
        return dict(zip(columns, trainee))

    def create_tab_content(self, tab, tab_type, trainee_details):
        if tab_type == "profile":
            self.create_profile_tab(tab, trainee_details)
        elif tab_type == "exams":
            self.create_exams_tab(tab, trainee_details)
        elif tab_type == "results":
            self.create_results_tab(tab, trainee_details)

    def create_profile_tab(self, tab, trainee_details):
        # Create frame for profile details
        frame = ctk.CTkFrame(tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Profile details
        profile_details = [
            ("Name", trainee_details['name']),
            ("ID Number", trainee_details['id_no']),
            ("ULI", trainee_details['uli']),
            ("Batch Year", trainee_details['batch_year']),
            ("Trainer", trainee_details['trainer_name']),
            ("Status", trainee_details['status'] or "Active"),
            ("Exams Taken", str(trainee_details['exams_taken']))
        ]

        for label, value in profile_details:
            detail_frame = ctk.CTkFrame(frame)
            detail_frame.pack(fill="x", padx=10, pady=5)
            
            label_widget = ctk.CTkLabel(
                detail_frame, 
                text=f"{label}:", 
                width=150, 
                anchor="w"
            )
            label_widget.pack(side="left", padx=5)
            
            value_widget = ctk.CTkLabel(
                detail_frame, 
                text=value, 
                width=250
            )
            value_widget.pack(side="left")

    def create_exams_tab(self, tab, trainee_details):
        # Create frame for exams
        frame = ctk.CTkFrame(tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Fetch available exams for the trainee's batch
        conn = sqlite3.connect('exam_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, module_no, num_items, time_limit 
            FROM exams 
            WHERE batch_id = ?
        """, (trainee_details['batch_id'],))
        
        exams = cursor.fetchall()
        conn.close()

        # Create Treeview for exams
        columns = ["Title", "Module", "Items", "Time Limit"]
        table = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=100, anchor='center')
        
        # Populate exams
        for exam in exams:
            table.insert('', 'end', values=(exam[1], exam[2], exam[3], f"{exam[4]} mins"))
        
        table.pack(expand=True, fill="both", padx=10, pady=10)

        # Take Exam button
        take_exam_button = ctk.CTkButton(
            frame, 
            text="Take Selected Exam", 
            command=self.take_exam
        )
        take_exam_button.pack(pady=10)

    def create_results_tab(self, tab, trainee_details):
        # Create frame for results
        frame = ctk.CTkFrame(tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Fetch exam results
        conn = sqlite3.connect('exam_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.title, r.competency, r.date_taken, r.remarks
            FROM results r
            JOIN exams e ON r.exam_id = e.id
            WHERE r.trainee_id = ?
        """, (trainee_details['id'],))
        
        results = cursor.fetchall()
        conn.close()

        # Create Treeview for results
        columns = ["Exam", "Competency", "Date Taken", "Remarks"]
        table = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=100, anchor='center')
        
        # Populate results
        for result in results:
            table.insert('', 'end', values=result)
        
        table.pack(expand=True, fill="both", padx=10, pady=10)

    def take_exam(self):
        """Implement exam taking functionality"""
        # Get selected exam from treeview
        selected_item = self.exams_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an exam to take")
            return

        exam_details = self.exams_table.item(selected_item[0])['values']
        exam_id = self.available_exams[exam_details[0]]  # Map exam title to ID

        # Open exam window
        exam_window = ctk.CTkToplevel(self.master)
        exam_window.title(f"Exam: {exam_details[0]}")
        exam_window.geometry("600x500")

        # Fetch exam questions
        questions = self.db_manager.get_exam_questions(exam_id)
        
        # Create exam interface
        exam_frame = ctk.CTkScrollableFrame(exam_window)
        exam_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Render questions dynamically
        answers = {}
        for idx, (q_id, question_text, correct_answer, points) in enumerate(questions, 1):
            question_label = ctk.CTkLabel(exam_frame, text=f"{idx}. {question_text}")
            question_label.pack(pady=(10, 5))

            # Multiple choice or true/false
            answer_var = tk.StringVar()
            options = [correct_answer, "Incorrect Option 1", "Incorrect Option 2", "Incorrect Option 3"]
            for option in options:
                radio_btn = ctk.CTkRadioButton(
                    exam_frame, 
                    text=option, 
                    variable=answer_var, 
                    value=option
                )
                radio_btn.pack(pady=2)
            
            answers[q_id] = answer_var

        def submit_exam():
            # Calculate score
            total_score = 0
            for q_id, (_, _, correct_answer, points) in enumerate(questions):
                if answers[q_id].get() == correct_answer:
                    total_score += points
            
            # Submit result
            self.db_manager.submit_exam_result(
                trainee_id=self.trainee_details['id'], 
                exam_id=exam_id, 
                score=total_score
            )
            
            messagebox.showinfo("Exam Completed", f"Your score: {total_score}")
            exam_window.destroy()

        submit_button = ctk.CTkButton(exam_frame, text="Submit Exam", command=submit_exam)
        submit_button.pack(pady=20)

    def logout(self):
        # Destroy trainee frame and return to login
        self.trainee_frame.destroy()
        self.logout_callback()