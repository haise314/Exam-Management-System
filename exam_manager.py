import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import time
from config import THEME, BUTTON_COLORS

class ExamManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_exam = None
        self.current_questions = []
        self.answers = {}
        self.start_time = None
        self.remaining_time = 0
        self.timer_id = None

    def start_exam(self, exam_id, trainee_id, callback=None):
        """Start an exam session with validation"""
        # Validate exam attempt
        validation = self.db_manager.validate_exam_attempt(trainee_id, exam_id)
        if not validation['can_take']:
            messagebox.showerror("Cannot Take Exam", validation['message'])
            return False

        # Get exam details and questions
        exam_details = self.db_manager.get_exam_details(exam_id)
        if not exam_details:
            messagebox.showerror("Error", "Failed to load exam details")
            return False

        questions = self.db_manager.get_exam_questions(exam_id)
        if not questions:
            messagebox.showerror("Error", "No questions found for this exam")
            return False

        # Initialize exam session
        self.current_exam = exam_details
        self.current_questions = questions
        self.answers = {}
        self.start_time = datetime.now()
        self.remaining_time = exam_details['time_limit'] * 60  # Convert to seconds
        
        if callback:
            callback()
        return True

    def create_exam_window(self, parent, trainee_id, completion_callback=None):
        """Create the exam window with improved UI and close protection"""
        if not self.current_exam or not self.current_questions:
            messagebox.showerror("Error", "No active exam session")
            return None

        # Create exam window
        exam_window = ctk.CTkToplevel(parent)
        exam_window.title(f"Exam: {self.current_exam['title']}")
        exam_window.geometry("1000x800")
        exam_window.resizable(True, True)
        
        # Prevent window closing with X button
        def on_close():
            if messagebox.askyesno(
                "Confirm Exit",
                "Are you sure you want to exit? This will end your exam session and your progress will be lost.",
                icon="warning"
            ):
                self.end_exam(trainee_id, force=True)
                exam_window.destroy()
                if completion_callback:
                    completion_callback()
        
        exam_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Ensure window stays on top and modal
        exam_window.transient(parent)
        exam_window.grab_set()
        
        # Store trainee ID for forced submission
        self.current_trainee_id = trainee_id

        # Create main container
        main_container = ctk.CTkFrame(exam_window, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # Exam header
        header = ctk.CTkFrame(
            main_container,
            fg_color=THEME["colors"]["primary_light"],
            corner_radius=8
        )
        header.pack(fill="x", pady=(0, 20))

        # Exam title and info
        title_label = ctk.CTkLabel(
            header,
            text=self.current_exam['title'],
            font=THEME["fonts"]["heading"],
            text_color=THEME["colors"]["text"]
        )
        title_label.pack(pady=(10, 5))

        info_text = f"Module {self.current_exam['module_no']} • {self.current_exam['num_items']} Items"
        info_label = ctk.CTkLabel(
            header,
            text=info_text,
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text_secondary"]
        )
        info_label.pack(pady=(0, 5))

        # Timer display
        self.timer_label = ctk.CTkLabel(
            header,
            text="Time Remaining: --:--",
            font=THEME["fonts"]["subheading"],
            text_color=THEME["colors"]["primary"]
        )
        self.timer_label.pack(pady=(0, 10))

        # Create scrollable frame for questions
        question_container = ctk.CTkScrollableFrame(main_container)
        question_container.pack(expand=True, fill="both", pady=(0, 20))

        # Add questions
        for idx, question in enumerate(self.current_questions, 1):
            self._create_question_widget(
                question_container, 
                idx, 
                question[1],  # question text
                question[2],  # correct_answer string
                question[0]   # question id
            )

        # Create bottom button bar
        button_bar = ctk.CTkFrame(main_container, fg_color="transparent")
        button_bar.pack(fill="x", pady=(0, 10))

        # Submit button
        submit_btn = ctk.CTkButton(
            button_bar,
            text="Submit Exam",
            font=THEME["fonts"]["body"],
            fg_color=THEME["colors"]["primary"],
            hover_color=THEME["colors"]["primary_hover"],
            command=lambda: self._handle_submit(exam_window, trainee_id, completion_callback)
        )
        submit_btn.pack(side="right", padx=5)

        # Start timer
        self._update_timer(exam_window)

        return exam_window

    def _create_question_widget(self, parent, number, text, options_str, q_id):
        """Create a question widget with options"""
        # Question frame
        q_frame = ctk.CTkFrame(
            parent,
            fg_color=THEME["colors"]["surface"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["colors"]["secondary"]
        )
        q_frame.pack(fill="x", padx=10, pady=5)

        # Question number and text
        q_label = ctk.CTkLabel(
            q_frame,
            text=f"Question {number}",
            font=THEME["fonts"]["subheading"],
            text_color=THEME["colors"]["primary"]
        )
        q_label.pack(anchor="w", padx=15, pady=(10, 5))

        text_label = ctk.CTkLabel(
            q_frame,
            text=text,
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text"],
            wraplength=800,
            justify="left"
        )
        text_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Parse options
        options = options_str.split('|')
        option_var = tk.StringVar()
        
        # Options container
        options_frame = ctk.CTkFrame(q_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=15, pady=(0, 10))

        for option in options:
            letter = option[1] if option.startswith('*') else option[0]
            text = option[3:] if option.startswith('*') else option[2:]
            
            # Option container
            option_container = ctk.CTkFrame(
                options_frame,
                fg_color="transparent",
                height=40
            )
            option_container.pack(fill="x", pady=2)
            
            radio_btn = ctk.CTkRadioButton(
                option_container,
                text=f"{letter}. {text}",
                variable=option_var,
                value=letter,
                font=THEME["fonts"]["body"],
                text_color=THEME["colors"]["text"],
                fg_color=THEME["colors"]["primary"]
            )
            radio_btn.pack(side="left", padx=15)

        # Store the variable for later access
        self.answers[q_id] = option_var

    def _update_timer(self, window):
        """Update the timer display"""
        if self.remaining_time > 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.timer_label.configure(
                text=f"Time Remaining: {minutes:02d}:{seconds:02d}"
            )
            self.remaining_time -= 1
            self.timer_id = window.after(1000, lambda: self._update_timer(window))
        else:
            self._handle_timeout(window)

    def _handle_timeout(self, window):
        """Handle exam timeout"""
        messagebox.showwarning(
            "Time's Up",
            "The exam time has expired. Your answers will be submitted automatically."
        )
        self._submit_exam(window)

    def _handle_submit(self, window, trainee_id, callback=None):
        """Handle exam submission"""
        if messagebox.askyesno("Confirm Submission", 
                              "Are you sure you want to submit your exam?"):
            # Get all answers
            answers = {q_id: var.get() for q_id, var in self.answers.items()}
            
            # Check for unanswered questions
            unanswered = sum(1 for ans in answers.values() if not ans)
            if unanswered > 0:
                if not messagebox.askyesno(
                    "Unanswered Questions",
                    f"You have {unanswered} unanswered question(s). "
                    "Do you still want to submit?"
                ):
                    return

            try:
                # Calculate time spent
                time_spent = int((datetime.now() - self.start_time).total_seconds())
                
                # Submit exam
                result = self.db_manager.submit_exam_result(
                    trainee_id,
                    self.current_exam['id'],
                    answers,
                    time_spent
                )
                
                # Update trainee status
                self.db_manager.update_trainee_status(trainee_id)
                
                # Show result
                status = "Passed" if result['percentage'] >= 75 else "Failed"
                messagebox.showinfo(
                    "Exam Complete",
                    f"Your score: {result['score']}/{result['total_items']}\n"
                    f"Percentage: {result['percentage']:.1f}%\n"
                    f"Status: {status}"
                )
                
                # Clean up
                if self.timer_id:
                    window.after_cancel(self.timer_id)
                window.destroy()
                
                if callback:
                    callback(result)
                    
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to submit exam: {str(e)}"
                )

    def _submit_exam(self, window):
        """Force submit the exam"""
        # Get all answers, using empty string for unanswered questions
        answers = {q_id: var.get() or '' for q_id, var in self.answers.items()}
        
        try:
            # Calculate time spent (use full time for timeout)
            time_spent = self.current_exam['time_limit'] * 60
            
            # Submit exam
            result = self.db_manager.submit_exam_result(
                self.current_trainee_id,
                self.current_exam['id'],
                answers,
                time_spent
            )
            
            # Clean up
            if self.timer_id:
                window.after_cancel(self.timer_id)
            window.destroy()
            
            # Show result
            status = "Passed" if result['percentage'] >= 75 else "Failed"
            messagebox.showinfo(
                "Exam Complete",
                f"Your score: {result['score']}/{result['total_items']}\n"
                f"Percentage: {result['percentage']:.1f}%\n"
                f"Status: {status}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to submit exam: {str(e)}"
            )

    def end_exam(self, trainee_id, force=False):
        """End exam session with optional force submit"""
        try:
            if force:
                # Get all answers, using empty string for unanswered
                answers = {q_id: var.get() or '' for q_id, var in self.answers.items()}
                
                # Calculate time spent (from start time to now)
                time_spent = int((datetime.now() - self.start_time).total_seconds())
                
                # Submit exam
                self.db_manager.submit_exam_result(
                    trainee_id,
                    self.current_exam['id'],
                    answers,
                    time_spent
                )
            
            # Clean up
            self.current_exam = None
            self.current_questions = []
            self.answers = {}
            self.start_time = None
            self.remaining_time = 0
            self.timer_id = None
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to end exam session: {str(e)}"
            )

