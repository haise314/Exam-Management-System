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
        self.trainee_details = None

        # Update main frame styling
        self.trainee_frame = ctk.CTkFrame(
            master,
            fg_color=THEME["colors"]["background"]
        )
        self.trainee_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Fetch trainee details
        self.trainee_details = self.get_trainee_details()
        if not self.trainee_details:
            messagebox.showerror("Error", "Unable to retrieve trainee details")
            self.logout()
            return
            
        self.trainee_id = self.trainee_details['id']

        # Update title styling
        title_label = ctk.CTkLabel(
            self.trainee_frame,
            text=f"Trainee Dashboard - {self.trainee_details['name']}",
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

        # Create tabs
        tabs = ["Profile", "Exams", "Results"]
        for tab_name in tabs:
            tab = self.tabview.add(tab_name)
            self.create_tab_content(tab, tab_name.lower())

        # Set default tab
        self.tabview.set("Profile")

        # Update logout button styling
        logout_button = ctk.CTkButton(
            self.trainee_frame,
            text="Logout",
            command=self.logout,
            fg_color=THEME["colors"]["primary"],
            hover_color=THEME["colors"]["primary_hover"]
        )
        logout_button.pack(pady=10)
        
    def get_trainee_details(self):
        # Fetch trainee details from database using the db_manager
        try:
            conn = sqlite3.connect('exam_management.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM trainees 
                WHERE id_no = ?
            """, (self.username,))
            
            trainee = cursor.fetchone()
            
            if not trainee:
                return None
                
            # Convert to dictionary for easy access
            columns = [
                'id', 'name', 'id_no', 'uli', 'batch_year', 
                'trainer_name', 'exams_taken', 'status', 'remarks', 'batch_id'
            ]
            return dict(zip(columns, trainee))
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch trainee details: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    def create_tab_content(self, tab, tab_type):
        if tab_type == "profile":
            self.create_profile_tab(tab)
        elif tab_type == "exams":
            self.create_exams_tab(tab)
        elif tab_type == "results":
            self.create_results_tab(tab)

    def create_profile_tab(self, tab):
        # Create frame for profile details
        frame = ctk.CTkFrame(tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Profile details
        profile_details = [
            ("Name", self.trainee_details['name']),
            ("ID Number", self.trainee_details['id_no']),
            ("ULI", self.trainee_details['uli'] or "Not assigned"),
            ("Batch Year", self.trainee_details['batch_year']),
            ("Trainer", self.trainee_details['trainer_name'] or "Not assigned"),
            ("Status", self.trainee_details['status'] or "Active"),
            ("Exams Taken", str(self.trainee_details['exams_taken'] or 0))
        ]

        for label, value in profile_details:
            detail_frame = ctk.CTkFrame(frame, fg_color="transparent")
            detail_frame.pack(fill="x", padx=10, pady=5)
            
            label_widget = ctk.CTkLabel(
                detail_frame, 
                text=f"{label}:", 
                width=150, 
                anchor="w",
                font=("Helvetica", 12, "bold")
            )
            label_widget.pack(side="left", padx=5)
            
            value_widget = ctk.CTkLabel(
                detail_frame, 
                text=value, 
                anchor="w",
                font=("Helvetica", 12)
            )
            value_widget.pack(side="left", fill="x", expand=True)

    def create_exams_tab(self, tab):
        # Main container for exams tab
        exams_container = ctk.CTkFrame(tab, fg_color="transparent")
        exams_container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header section
        header_frame = ctk.CTkFrame(exams_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Available Exams",
            font=("Helvetica", 16, "bold"),
            text_color=THEME["colors"]["text"]
        )
        header_label.pack(side="left")
        
        refresh_button = ctk.CTkButton(
            header_frame,
            text="Refresh",
            command=self.refresh_exams,
            width=100,
            fg_color=THEME["colors"]["secondary"],
            hover_color=THEME["colors"]["secondary_hover"]
        )
        refresh_button.pack(side="right")

        # Table section
        table_frame = ctk.CTkFrame(exams_container)
        table_frame.pack(expand=True, fill="both")
        
        # Create modern table style
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
            relief="flat",
            font=("Helvetica", 10, "bold")
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", THEME["colors"]["primary_light"])],
            foreground=[("selected", THEME["colors"]["text"])]
        )

        # Create exams table with columns
        columns = ("ID", "Title", "Module", "Items", "Time Limit", "Status")
        self.exams_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview",
            selectmode="browse"
        )

        # Configure the ID column to be hidden but keep the data
        self.exams_table.heading("ID", text="ID")
        self.exams_table.column("ID", width=0, stretch=False)

        # Configure visible columns
        for col in columns[1:]:  # Skip ID column which is hidden
            self.exams_table.heading(col, text=col)
            width = 150 if col == "Title" else 100
            self.exams_table.column(col, width=width, anchor='center')

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.exams_table.yview)
        self.exams_table.configure(yscrollcommand=y_scrollbar.set)

        # Pack table and scrollbar
        self.exams_table.pack(side="left", expand=True, fill="both", padx=(5, 0))
        y_scrollbar.pack(side="right", fill="y")

        # Action button section
        action_frame = ctk.CTkFrame(exams_container, fg_color="transparent")
        action_frame.pack(fill="x", pady=10)
        
        take_exam_btn = ctk.CTkButton(
            action_frame,
            text="Take Selected Exam",
            command=self.take_exam,
            fg_color=THEME["colors"]["primary"],
            hover_color=THEME["colors"]["primary_hover"],
            font=("Helvetica", 12, "bold")
        )
        take_exam_btn.pack(side="right", padx=10)
        
        # Populate exams immediately
        self.refresh_exams()

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

    def create_results_tab(self, tab):
        # Main container for results tab
        results_container = ctk.CTkFrame(tab, fg_color="transparent")
        results_container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header section
        header_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Your Exam Results",
            font=("Helvetica", 16, "bold"),
            text_color=THEME["colors"]["text"]
        )
        header_label.pack(side="left")
        
        refresh_button = ctk.CTkButton(
            header_frame,
            text="Refresh",
            command=self.refresh_results,
            width=100,
            fg_color=THEME["colors"]["secondary"],
            hover_color=THEME["colors"]["secondary_hover"]
        )
        refresh_button.pack(side="right")

        # Results table section
        table_frame = ctk.CTkFrame(results_container)
        table_frame.pack(expand=True, fill="both")
        
        # Create modern table style (reusing style from exams tab)
        style = ttk.Style()
        if not style.theme_names():  # Check if style exists already
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
                relief="flat",
                font=("Helvetica", 10, "bold")
            )
            style.map(
                "Custom.Treeview",
                background=[("selected", THEME["colors"]["primary_light"])],
                foreground=[("selected", THEME["colors"]["text"])]
            )

        # Create results table
        columns = ("Exam", "Score", "Percentage", "Date Taken", "Time Spent", "Status")
        self.results_table = ttk.Treeview(
            table_frame, 
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )

        # Configure columns
        for col in columns:
            self.results_table.heading(col, text=col)
            width = 150 if col in ("Exam", "Date Taken") else 100
            self.results_table.column(col, width=width, anchor='center')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.results_table.yview
        )
        self.results_table.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        self.results_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load results
        self.refresh_results()
        
    def refresh_exams(self):
        try:
            self.exams_table.delete(*self.exams_table.get_children())
            exams = self.db_manager.get_available_exams(self.trainee_id)
            for exam in exams:
                self.exams_table.insert('', 'end', values=(exam['id'], exam['title'], exam['module_no'], 
                                                           exam['num_items'], f"{exam['time_limit']} mins", exam['status']))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exams: {str(e)}")

    def refresh_results(self):
        try:
            self.results_table.delete(*self.results_table.get_children())
            results = self.db_manager.get_trainee_results(self.trainee_id)

            # Ensure column order matches the database schema
            for result in results:
                self.results_table.insert('', 'end', values=(
                    result['exam_title'], 
                    f"{result['score']}/{result['total_items']}", 
                    f"{result['percentage']:.1f}%", 
                    result['date_taken'], 
                    f"{result['time_spent'] // 60}:{result['time_spent'] % 60:02d}", 
                    result['status']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load results: {str(e)}")

    def take_exam(self):
        selected = self.exams_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an exam")
            return
        exam_id = self.exams_table.item(selected[0])['values'][0]
        status = self.exams_table.item(selected[0])['values'][5]  # Status value
        
        # Check if exam has already been taken
        if status == 'Completed':
            messagebox.showerror("Error", "You have already taken this exam")
            return

        # Get exam details
        try:
            exam_details = self.db_manager.get_exam_details(exam_id)
            if not exam_details:
                messagebox.showerror("Error", "Could not load exam details")
                return
                
            # Get exam questions
            questions = self.db_manager.get_exam_questions(exam_id)
            if not questions:
                messagebox.showerror("Error", "This exam has no questions")
                return
                
            # Create exam window
            self.open_exam_window(exam_details, questions)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exam: {str(e)}")

    def open_exam_window(self, exam_details, questions):
        # Create a modal window for the exam
        exam_window = BaseModal(
            self.master,
            f"Exam: {exam_details['title']}",
            size="800x600"
        )
        
        # Create header area with exam info
        header_frame = ctk.CTkFrame(exam_window.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text=f"Module: {exam_details['module_no']} - {exam_details['title']}",
            font=("Helvetica", 16, "bold")
        ).pack(anchor="w")
        
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Total Items: {exam_details['num_items']}",
            font=("Helvetica", 12)
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Time Limit: {exam_details['time_limit']} minutes",
            font=("Helvetica", 12)
        ).pack(side="left")

        # Initialize timer
        remaining_time = exam_details['time_limit'] * 60  # Convert to seconds
        start_time = datetime.now()  # Record start time
        
        timer_frame = ctk.CTkFrame(
            exam_window.container,
            fg_color=THEME["colors"]["primary_light"],
            corner_radius=8
        )
        timer_frame.pack(fill="x", padx=10, pady=5)
        
        timer_label = ctk.CTkLabel(
            timer_frame,
            text="Time Remaining: 00:00",
            font=("Helvetica", 14, "bold"),
            text_color=THEME["colors"]["primary"]
        )
        timer_label.pack(pady=5)

        def update_timer():
            nonlocal remaining_time
            if remaining_time > 0 and not exam_window.winfo_exists():
                # Window was closed, stop the timer
                return
                
            if remaining_time > 0:
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                timer_label.configure(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")
                remaining_time -= 1
                exam_window.after(1000, update_timer)
            else:
                timer_label.configure(text="Time's Up!", text_color="red")
                messagebox.showwarning("Time's Up!", "Your time has expired. Submitting exam...")
                submit_exam()

        # Create scrollable question form
        answers = {}  # Dictionary to store answers: {question_id: answer_value}

        # Add questions to the form
        for i, q in enumerate(questions, 1):
            q_frame = ctk.CTkFrame(
                exam_window.scrollable_frame,
                fg_color=THEME["colors"]["surface"],
                corner_radius=8,
                border_width=1,
                border_color="#e0e0e0"
            )
            q_frame.pack(fill="x", pady=10, padx=10)
            
            # Question number and text
            question_header = ctk.CTkFrame(q_frame, fg_color="transparent")
            question_header.pack(fill="x", padx=10, pady=5)
            
            q_num_label = ctk.CTkLabel(
                question_header,
                text=f"Question {i}:",
                font=("Helvetica", 12, "bold"),
                width=80,
                anchor="w"
            )
            q_num_label.pack(side="left")
            
            q_text_label = ctk.CTkLabel(
                question_header,
                text=q[1],  # question_text
                wraplength=650,
                justify="left",
                anchor="w"
            )
            q_text_label.pack(side="left", fill="x", expand=True)

            # Parse options from the correct_answer field
            # Format: "*A:Option Text|B:Another Option|..."
            options_data = q[2].split('|')  # Split options
            correct_answer = None
            option_texts = {}
            
            for option_str in options_data:
                if option_str.startswith('*'):
                    # This is the correct answer
                    option_key = option_str[1]  # Skip the * character
                    correct_answer = option_key
                    option_text = option_str[3:]  # Skip the "*A:" part
                else:
                    option_key = option_str[0]  # Just the letter
                    option_text = option_str[2:]  # Skip the "A:" part
                
                option_texts[option_key] = option_text

            # Answer variable for radio buttons
            answer_var = tk.StringVar(value="")
            answers[q[0]] = answer_var
            
            # Options as radio buttons
            options_frame = ctk.CTkFrame(q_frame, fg_color="transparent")
            options_frame.pack(fill="x", padx=20, pady=5)
            
            for option_key in ['A', 'B', 'C', 'D']:
                if option_key in option_texts:
                    option_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
                    option_frame.pack(fill="x", pady=2)
                    
                    radio_btn = ctk.CTkRadioButton(
                        option_frame,
                        text=f"{option_key}. {option_texts[option_key]}",
                        variable=answer_var,
                        value=option_key,
                        font=("Helvetica", 12)
                    )
                    radio_btn.pack(side="left", padx=(20, 0), pady=3)

        # Actions area at the bottom
        actions_frame = ctk.CTkFrame(exam_window.container, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=10)

        def submit_exam():
            # Calculate time spent
            time_spent = int((datetime.now() - start_time).total_seconds())
            if time_spent > exam_details['time_limit'] * 60:
                time_spent = exam_details['time_limit'] * 60  # Cap at max time
            
            # Collect answers
            submitted_answers = {
                q_id: var.get() for q_id, var in answers.items()
            }
            
            # Check if all questions are answered
            unanswered = sum(1 for ans in submitted_answers.values() if not ans)
            if unanswered > 0:
                confirm = messagebox.askyesno(
                    "Confirmation", 
                    f"You have {unanswered} unanswered question(s). Are you sure you want to submit?"
                )
                if not confirm:
                    return
            
            try:
                # Submit exam results to database
                result = self.db_manager.submit_exam_result(
                    self.trainee_id,
                    exam_details['id'],
                    submitted_answers,
                    time_spent
                )
                
                if result:
                    status = "Passed" if result['percentage'] >= 75 else "Failed"
                    color = "#4caf50" if status == "Passed" else "#f44336"
                    
                    # Show result summary
                    result_window = BaseModal(
                        self.master,
                        "Exam Result",
                        size="400x300"
                    )
                    
                    ctk.CTkLabel(
                        result_window.container,
                        text="Exam Completed!",
                        font=("Helvetica", 18, "bold")
                    ).pack(pady=10)
                    
                    ctk.CTkLabel(
                        result_window.container,
                        text=f"Your Score: {result['score']}/{result['total_items']}",
                        font=("Helvetica", 14)
                    ).pack(pady=5)
                    
                    ctk.CTkLabel(
                        result_window.container,
                        text=f"Percentage: {result['percentage']:.1f}%",
                        font=("Helvetica", 14)
                    ).pack(pady=5)
                    
                    ctk.CTkLabel(
                        result_window.container,
                        text=f"Status: {status}",
                        font=("Helvetica", 16, "bold"),
                        text_color=color
                    ).pack(pady=10)
                    
                    ctk.CTkButton(
                        result_window.container,
                        text="OK",
                        command=result_window.destroy,
                        fg_color=THEME["colors"]["primary"]
                    ).pack(pady=20)
                    
                    # Close exam window
                    exam_window.destroy()
                    
                    # Refresh both exams and results tabs
                    self.refresh_exams()
                    self.refresh_results()
                else:
                    messagebox.showerror("Error", "Failed to submit exam")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to submit exam: {str(e)}")

        # Submit button
        submit_btn = ctk.CTkButton(
            actions_frame,
            text="Submit Exam",
            command=submit_exam,
            fg_color=THEME["colors"]["primary"],
            hover_color=THEME["colors"]["primary_hover"],
            font=("Helvetica", 14, "bold"),
            height=40
        )
        submit_btn.pack(side="right", padx=10)

        # Start timer after UI is created
        update_timer()
    
    def logout(self):
        # Destroy trainee frame and return to login
        if hasattr(self, 'trainee_frame'):
            self.trainee_frame.destroy()
        self.logout_callback()