import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import THEME, BUTTON_COLORS
from exam_manager import ExamManager
from components import LoadingIndicator

class TraineeDashboard:
    def __init__(self, master, db_manager, trainee_id, logout_callback):
        self.master = master
        self.db_manager = db_manager
        self.trainee_id = trainee_id
        self.logout_callback = logout_callback
        self.exam_manager = ExamManager(db_manager)
        
        # Create main container
        self.main_container = ctk.CTkFrame(master, fg_color="#f5f5f5")
        self.main_container.pack(expand=True, fill="both")
        
        # Create sidebar
        self.create_sidebar()
        
        # Create content area
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="#ffffff")
        self.content_frame.pack(side="left", expand=True, fill="both", padx=20, pady=20)
        
        # Load initial view
        self.show_overview()
        
        # Configure Treeview style
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure Treeview colors
        self.style.configure(
            "Treeview",
            background=THEME["colors"]["surface"],
            foreground=THEME["colors"]["text"],
            fieldbackground=THEME["colors"]["surface"],
            font=THEME["fonts"]["body"]
        )
        
        self.style.configure(
            "Treeview.Heading",
            background=THEME["colors"]["primary_light"],
            foreground=THEME["colors"]["text"],
            font=THEME["fonts"]["body"]
        )
        
        # Configure selection colors
        self.style.map(
            'Treeview',
            background=[('selected', THEME["colors"]["primary"])],
            foreground=[('selected', '#ffffff')]
        )

    def create_sidebar(self):
        """Create sidebar with navigation"""
        sidebar = ctk.CTkFrame(
            self.main_container,
            width=200,
            corner_radius=0,
            fg_color=THEME["colors"]["primary"]
        )
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)

        # Dashboard title
        title_label = ctk.CTkLabel(
            sidebar,
            text="Trainee Dashboard",
            font=THEME["fonts"]["heading"],
            text_color="white"
        )
        title_label.pack(pady=20)

        # Navigation buttons
        nav_buttons = [
            ("Overview", self.show_overview),
            ("Available Exams", self.show_available_exams),
            ("My Results", self.show_results),
            ("Progress Report", self.show_progress)
        ]

        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                width=180,
                height=40,
                corner_radius=0,
                fg_color="transparent",
                text_color="white",
                hover_color=("gray70", "gray30")
            )
            btn.pack(pady=5)

        # Logout button at bottom
        logout_button = ctk.CTkButton(
            sidebar,
            text="Logout",
            command=self.logout,
            width=180,
            height=40
        )
        logout_button.pack(side="bottom", pady=20)

    def clear_content(self):
        """Clear current content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_overview(self):
        """Show trainee overview with progress summary"""
        self.clear_content()
        
        try:
            # Get trainee progress
            progress = self.db_manager.get_trainee_progress(self.trainee_id)
            
            # Create overview container
            overview = ctk.CTkFrame(
                self.content_frame,
                fg_color=THEME["colors"]["surface"]
            )
            overview.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Header with trainee info
            header = ctk.CTkFrame(
                overview,
                fg_color=THEME["colors"]["primary_light"],
                corner_radius=8
            )
            header.pack(fill="x", padx=20, pady=20)
            
            ctk.CTkLabel(
                header,
                text=f"Welcome, {progress['trainee_name']}",
                font=THEME["fonts"]["heading"],
                text_color=THEME["colors"]["text"]
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                header,
                text=f"Batch Year: {progress['batch_year']} • Status: {progress['status']}",
                font=THEME["fonts"]["body"],
                text_color=THEME["colors"]["text_secondary"]
            ).pack(pady=(0, 10))
            
            # Progress statistics
            stats_frame = ctk.CTkFrame(overview, fg_color="transparent")
            stats_frame.pack(fill="x", padx=20, pady=10)
            stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Create stat boxes
            self._create_stat_box(
                stats_frame, 0,
                "Completion Rate",
                f"{progress['completion_percentage']:.1f}%",
                f"{progress['completed_exams']}/{progress['total_exams']} Exams"
            )
            
            self._create_stat_box(
                stats_frame, 1,
                "Passing Rate",
                f"{progress['passing_percentage']:.1f}%",
                f"{progress['passed_exams']}/{progress['total_exams']} Passed"
            )
            
            # Recent exams section
            recent_frame = ctk.CTkFrame(overview, fg_color="transparent")
            recent_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                recent_frame,
                text="Recent Exams",
                font=THEME["fonts"]["subheading"],
                text_color=THEME["colors"]["text"]
            ).pack(anchor="w", pady=(0, 10))
            
            # Create table for recent exams
            columns = ("Title", "Status", "Score", "Date")
            tree = ttk.Treeview(recent_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # Add recent exams
            for exam in progress['exams'][-5:]:  # Show last 5 exams
                if exam['date_taken']:
                    tree.insert("", "end", values=(
                        exam['title'],
                        exam['status'],
                        f"{exam['score_percentage']:.1f}%",
                        exam['date_taken']
                    ))
            
            tree.pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load overview: {str(e)}")

    def _create_stat_box(self, parent, column, title, main_value, sub_value):
        """Create a statistics box"""
        box = ctk.CTkFrame(
            parent,
            fg_color=THEME["colors"]["surface"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["colors"]["secondary"]
        )
        box.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            box,
            text=title,
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text_secondary"]
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            box,
            text=main_value,
            font=THEME["fonts"]["heading"],
            text_color=THEME["colors"]["primary"]
        ).pack()
        
        ctk.CTkLabel(
            box,
            text=sub_value,
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text_secondary"]
        ).pack(pady=(5, 10))

    def show_available_exams(self):
        """Show available exams for the trainee"""
        self.clear_content()
        
        try:
            # Get available exams
            exams = self.db_manager.get_available_exams(self.trainee_id)
            
            # Create container
            container = ctk.CTkFrame(
                self.content_frame,
                fg_color=THEME["colors"]["surface"]
            )
            container.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Header
            ctk.CTkLabel(
                container,
                text="Available Exams",
                font=THEME["fonts"]["heading"],
                text_color=THEME["colors"]["text"]
            ).pack(pady=20)
            
            # Create exam cards
            for exam in exams:
                self._create_exam_card(container, exam)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exams: {str(e)}")

    def _create_exam_card(self, parent, exam):
        """Create a card for an exam"""
        card = ctk.CTkFrame(
            parent,
            fg_color=THEME["colors"]["surface"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["colors"]["secondary"]
        )
        card.pack(fill="x", padx=20, pady=10)
        
        # Title and module
        ctk.CTkLabel(
            card,
            text=exam['title'],
            font=THEME["fonts"]["subheading"],
            text_color=THEME["colors"]["text"]
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            card,
            text=f"Module {exam['module_no']} • {exam['num_items']} Items • {exam['time_limit']} Minutes",
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text_secondary"]
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Status and action button
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        status_label = ctk.CTkLabel(
            button_frame,
            text=f"Status: {exam['status']}",
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text_secondary"]
        )
        status_label.pack(side="left")
        
        if exam['status'] == 'Not Taken':
            take_btn = ctk.CTkButton(
                button_frame,
                text="Take Exam",
                font=THEME["fonts"]["body"],
                command=lambda: self.start_exam(exam['id'])
            )
            take_btn.pack(side="right")

    def start_exam(self, exam_id):
        """Start an exam session"""
        if self.exam_manager.start_exam(exam_id, self.trainee_id):
            exam_window = self.exam_manager.create_exam_window(
                self.master,
                self.trainee_id,
                self.on_exam_complete
            )

    def on_exam_complete(self, result=None):
        """Handle exam completion"""
        self.show_overview()  # Refresh overview

    def show_results(self):
        """Show exam results with export options"""
        self.clear_content()
        
        try:
            # Get exam history
            history = self.db_manager.get_trainee_exam_history(self.trainee_id)
            
            # Create container
            container = ctk.CTkFrame(
                self.content_frame,
                fg_color=THEME["colors"]["surface"]
            )
            container.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Header with overall stats and export options
            header = ctk.CTkFrame(
                container,
                fg_color=THEME["colors"]["primary_light"],
                corner_radius=8
            )
            header.pack(fill="x", padx=20, pady=20)
            
            # Add export toolbar
            toolbar = ctk.CTkFrame(header, fg_color="transparent")
            toolbar.pack(fill="x", padx=15, pady=(0, 10))
            
            # Export buttons
            csv_btn = ctk.CTkButton(
                toolbar,
                text="Export CSV",
                font=THEME["fonts"]["body"],
                fg_color=THEME["colors"]["secondary"],
                hover_color=THEME["colors"]["secondary_hover"],
                width=120,
                command=lambda: self._export_results('csv')
            )
            csv_btn.pack(side="right", padx=5)
            
            json_btn = ctk.CTkButton(
                toolbar,
                text="Export JSON",
                font=THEME["fonts"]["body"],
                fg_color=THEME["colors"]["secondary"],
                hover_color=THEME["colors"]["secondary_hover"],
                width=120,
                command=lambda: self._export_results('json')
            )
            json_btn.pack(side="right", padx=5)
            
            # Existing results view code...
            stats = history['overall_stats']
            ctk.CTkLabel(
                header,
                text="Your Performance",
                font=THEME["fonts"]["heading"],
                text_color=THEME["colors"]["text"]
            ).pack(pady=(10, 5))
            
            stats_text = (
                f"Exams Attempted: {stats['exams_attempted']} • "
                f"Exams Passed: {stats['exams_passed']} • "
                f"Overall Average: {stats['overall_average']:.1f}%"
            )
            ctk.CTkLabel(
                header,
                text=stats_text,
                font=THEME["fonts"]["body"],
                text_color=THEME["colors"]["text_secondary"]
            ).pack(pady=(0, 10))
            
            # Results table
            columns = ("Module", "Exam", "Best Score", "Last Score", "Attempts", "Status")
            tree = ttk.Treeview(container, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # Add results
            for exam in history['exam_history']:
                tree.insert("", "end", values=(
                    exam['module_no'],
                    exam['title'],
                    f"{exam['best_score']:.1f}%",
                    f"{exam['last_score']:.1f}%",
                    exam['attempts'],
                    "Passed" if exam['passed'] else "Failed"
                ))
            
            tree.pack(fill="both", expand=True, padx=20, pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load results: {str(e)}")

    def _export_results(self, format):
        """Handle exporting results with loading indicator"""
        try:
            # Create and show loading indicator
            loading = LoadingIndicator(self.content_frame, "Preparing export...")
            loading.show()
            
            # Update UI and process in chunks
            def process_export():
                try:
                    # Get export data
                    export_data = self.db_manager.export_trainee_results(self.trainee_id, format)
                    
                    # Ask user where to save the file
                    from tkinter import filedialog
                    file_types = [('CSV files', '*.csv')] if format == 'csv' else [('JSON files', '*.json')]
                    filename = filedialog.asksaveasfilename(
                        defaultextension=f".{format}",
                        filetypes=file_types,
                        title="Save Export As"
                    )
                    
                    if filename:  # User didn't cancel
                        loading.update_text("Saving file...")
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(export_data)
                        messagebox.showinfo(
                            "Export Complete",
                            f"Results exported successfully to {filename}"
                        )
                finally:
                    loading.hide()
            
            # Schedule the export process
            self.master.after(100, process_export)
                
        except Exception as e:
            loading.hide()
            messagebox.showerror(
                "Export Error",
                f"Failed to export results: {str(e)}"
            )

    def show_progress(self):
        """Show detailed progress report with export options"""
        self.clear_content()
        
        try:
            # Get trainee progress
            progress = self.db_manager.get_trainee_progress(self.trainee_id)
            
            # Create container
            container = ctk.CTkFrame(
                self.content_frame,
                fg_color=THEME["colors"]["surface"]
            )
            container.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Progress overview with export option
            overview = ctk.CTkFrame(
                container,
                fg_color=THEME["colors"]["primary_light"],
                corner_radius=8
            )
            overview.pack(fill="x", padx=20, pady=20)
            
            # Add export button to overview
            export_btn = ctk.CTkButton(
                overview,
                text="Export Progress Report",
                font=THEME["fonts"]["body"],
                fg_color=THEME["colors"]["secondary"],
                hover_color=THEME["colors"]["secondary_hover"],
                width=160,
                command=self._export_progress
            )
            export_btn.pack(side="top", pady=(10, 0))
            
            # Progress overview header
            ctk.CTkLabel(
                overview,
                text="Progress Overview",
                font=THEME["fonts"]["heading"],
                text_color=THEME["colors"]["text"]
            ).pack(pady=(10, 5))
            
            progress_text = (
                f"Completed: {progress['completed_exams']}/{progress['total_exams']} "
                f"({progress['completion_percentage']:.1f}%) • "
                f"Passed: {progress['passed_exams']}/{progress['total_exams']} "
                f"({progress['passing_percentage']:.1f}%)"
            )
            ctk.CTkLabel(
                overview,
                text=progress_text,
                font=THEME["fonts"]["body"],
                text_color=THEME["colors"]["text_secondary"]
            ).pack(pady=(0, 10))
            
            # Progress bars
            self._create_progress_bar(
                container,
                "Completion Progress",
                progress['completion_percentage']
            )
            
            self._create_progress_bar(
                container,
                "Passing Progress",
                progress['passing_percentage']
            )
            
            # Detailed exam list
            ctk.CTkLabel(
                container,
                text="Exam Details",
                font=THEME["fonts"]["subheading"],
                text_color=THEME["colors"]["text"]
            ).pack(anchor="w", padx=20, pady=(20, 10))
            
            for exam in progress['exams']:
                self._create_exam_progress_card(container, exam)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load progress: {str(e)}")
            
    def _export_progress(self):
        """Handle exporting progress report with loading indicator"""
        try:
            # Create and show loading indicator
            loading = LoadingIndicator(self.content_frame, "Preparing progress report...")
            loading.show()
            
            def process_export():
                try:
                    # Get batch ID for the trainee
                    self.db_manager.connect()
                    self.db_manager.cursor.execute(
                        "SELECT batch_id FROM trainees WHERE id = ?",
                        (self.trainee_id,)
                    )
                    batch_id = self.db_manager.cursor.fetchone()[0]
                    self.db_manager.close()
                    
                    if not batch_id:
                        raise ValueError("Could not determine batch ID")
                    
                    loading.update_text("Generating report...")
                    # Get export data
                    export_data = self.db_manager.export_batch_report(batch_id)
                    
                    # Ask user where to save the file
                    from tkinter import filedialog
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        filetypes=[('CSV files', '*.csv')],
                        title="Save Progress Report As"
                    )
                    
                    if filename:  # User didn't cancel
                        loading.update_text("Saving report...")
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(export_data)
                        messagebox.showinfo(
                            "Export Complete",
                            f"Progress report exported successfully to {filename}"
                        )
                finally:
                    loading.hide()
            
            # Schedule the export process
            self.master.after(100, process_export)
                
        except Exception as e:
            if 'loading' in locals():
                loading.hide()
            messagebox.showerror(
                "Export Error",
                f"Failed to export progress report: {str(e)}"
            )

    def _create_progress_bar(self, parent, label, value):
        """Create a progress bar"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text"]
        ).pack(anchor="w")
        
        progress = ctk.CTkProgressBar(frame)
        progress.pack(fill="x", pady=5)
        progress.set(value / 100)
        
        ctk.CTkLabel(
            frame,
            text=f"{value:.1f}%",
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text_secondary"]
        ).pack(anchor="e")

    def _create_exam_progress_card(self, parent, exam):
        """Create a card showing exam progress"""
        card = ctk.CTkFrame(
            parent,
            fg_color=THEME["colors"]["surface"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["colors"]["secondary"]
        )
        card.pack(fill="x", padx=20, pady=5)
        
        # Title and status
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            header,
            text=exam['title'],
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text"]
        ).pack(side="left")
        
        status_color = THEME["colors"]["success"] if exam['status'] == 'Passed' else (
            THEME["colors"]["primary"] if exam['status'] == 'Not Taken' else
            THEME["colors"]["danger"]
        )
        
        ctk.CTkLabel(
            header,
            text=exam['status'],
            font=THEME["fonts"]["body"],
            text_color=status_color
        ).pack(side="right")
        
        # Score if exam was taken
        if exam['status'] != 'Not Taken':
            score_frame = ctk.CTkFrame(card, fg_color="transparent")
            score_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            ctk.CTkLabel(
                score_frame,
                text=f"Score: {exam['score_percentage']:.1f}%",
                font=THEME["fonts"]["body"],
                text_color=THEME["colors"]["text_secondary"]
            ).pack(side="left")
            
            if exam['date_taken']:
                ctk.CTkLabel(
                    score_frame,
                    text=f"Taken on: {exam['date_taken']}",
                    font=THEME["fonts"]["body"],
                    text_color=THEME["colors"]["text_secondary"]
                ).pack(side="right")

    def logout(self):
        """Handle logout"""
        self.main_container.destroy()
        self.logout_callback()