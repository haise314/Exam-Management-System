import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from config import THEME, BUTTON_COLORS
from components import BaseModal

class TraineeDashboard:
    def __init__(self, master, db_manager, username, logout_callback):
        self.master = master
        self.db_manager = db_manager
        self.username = username
        self.logout_callback = logout_callback

        # Update main frame styling
        self.trainee_frame = ctk.CTkFrame(
            master,
            fg_color=THEME["colors"]["background"]
        )
        self.trainee_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Update title styling
        title_label = ctk.CTkLabel(
            self.trainee_frame,
            text=f"Trainee Dashboard - {self.username}",
            font=THEME["fonts"]["heading"],
            text_color=THEME["colors"]["text"]
        )
        title_label.pack(pady=(20, 10))

        # Update tabview styling
        self.tabview = ctk.CTkTabview(
            self.trainee_frame,
            fg_color=THEME["colors"]["surface"]
        )
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        # Update logout button styling
        logout_button = ctk.CTkButton(
            self.trainee_frame,
            text="Logout",
            command=self.logout,
            fg_color=THEME["colors"]["primary"],
            hover_color=THEME["colors"]["primary_hover"]
        )
        logout_button.pack(pady=10)

        # Fetch trainee details
        trainee_details = self.get_trainee_details()

        # Create tabs
        tabs = ["Profile", "Exams", "Results"]
        for tab_name in tabs:
            tab = self.tabview.add(tab_name)
            self.create_tab_content(tab, tab_name.lower(), trainee_details)

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
        frame = ctk.CTkFrame(tab, fg_color=THEME["colors"]["surface"])
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create modern table style
        style = self.create_table_style()

        columns = ["Title", "Module", "Items", "Time Limit", "Status"]
        self.exams_table = ttk.Treeview(
            frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview"
        )

        for col in columns:
            self.exams_table.heading(col, text=col)
            self.exams_table.column(col, width=100, anchor='center')

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.exams_table.yview)
        self.exams_table.configure(yscrollcommand=y_scrollbar.set)

        # Pack table and scrollbar
        self.exams_table.pack(side="left", expand=True, fill="both", padx=(5, 0))
        y_scrollbar.pack(side="right", fill="y")

        # Populate table with available exams
        try:
            available_exams = self.db_manager.get_available_exams(trainee_details['id'])
            for exam in available_exams:
                values = (
                    exam['title'],
                    exam['module_no'],
                    exam['num_items'],
                    f"{exam['time_limit']} mins",
                    exam['status']
                )
                self.exams_table.insert('', 'end', values=values, tags=(exam['id'],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exams: {str(e)}")

        # Add take exam button (only enabled for 'Not Taken' exams)
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        take_exam_btn = ctk.CTkButton(
            button_frame,
            text="Take Exam",
            command=self.take_exam,
            fg_color=THEME["colors"]["primary"],
            hover_color=THEME["colors"]["primary_hover"]
        )
        take_exam_btn.pack(side="right", padx=5)

        # Bind selection event to enable/disable take exam button
        def on_select(event):
            selected = self.exams_table.selection()
            if selected:
                item = self.exams_table.item(selected[0])
                status = item['values'][-1]
                take_exam_btn.configure(state="normal" if status == "Not Taken" else "disabled")
            else:
                take_exam_btn.configure(state="disabled")

        self.exams_table.bind('<<TreeviewSelect>>', on_select)
        take_exam_btn.configure(state="disabled")  # Initially disabled

    def create_table_style(self):
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background=THEME["colors"]["surface"],
            foreground=THEME["colors"]["text"],
            rowheight=40,
            fieldbackground=THEME["colors"]["surface"]
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=THEME["colors"]["primary"],
            foreground="white",
            relief="flat"
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", THEME["colors"]["primary"])],
            foreground=[("selected", "white")]
        )
        return style

    def create_results_tab(self, tab, trainee_details):
        frame = ctk.CTkFrame(
            tab,
            fg_color=THEME["colors"]["surface"]
        )
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create styled table
        style = self.create_table_style()
        
        columns = ["Exam", "Score", "Percentage", "Date Taken", "Status"]
        table = ttk.Treeview(
            frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview"
        )
        
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=100, anchor='center')

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=y_scrollbar.set)
        
        table.pack(expand=True, fill="both", side="left")
        y_scrollbar.pack(fill="y", side="right")

    def take_exam(self):
        selected = self.exams_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exam")
            return

        exam_id = self.exams_table.item(selected[0])['values'][0]
        exam_details = self.db_manager.get_exam_details(exam_id)

        # Create exam window
        exam_window = BaseModal(
            self.master,
            f"Exam: {exam_details['title']}",
            size="800x600"
        )

        # Add timer
        remaining_time = exam_details['time_limit'] * 60  # Convert to seconds
        timer_label = ctk.CTkLabel(
            exam_window,
            text=f"Time Remaining: {remaining_time//60}:{remaining_time%60:02d}"
        )
        timer_label.pack(pady=10)

        # Create question form
        questions = self.db_manager.get_exam_questions(exam_id)
        answers = {}

        for q in questions:
            q_frame = ctk.CTkFrame(exam_window.scrollable_frame)
            q_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                q_frame,
                text=q['question'],
                wraplength=700
            ).pack(pady=5)

            answer_var = tk.StringVar()
            answers[q['id']] = answer_var

            for option in q['options']:
                ctk.CTkRadioButton(
                    q_frame,
                    text=option,
                    variable=answer_var,
                    value=option
                ).pack(pady=2)

        # Submit button
        ctk.CTkButton(
            exam_window,
            text="Submit",
            command=lambda: self.submit_exam(exam_id, answers, exam_window)
        ).pack(pady=20)

    def logout(self):
        # Destroy trainee frame and return to login
        self.trainee_frame.destroy()
        self.logout_callback()