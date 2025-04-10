import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
from config import THEME, BUTTON_COLORS
from components import BaseModal  # Add this import

class AdminDashboard:
    def __init__(self, master, db_manager, logout_callback):
        self.master = master
        self.db_manager = db_manager
        self.logout_callback = logout_callback
        self.current_tab = "trainers"
        self.selected_record_id = None

        # Create main container with light theme
        self.main_container = ctk.CTkFrame(master, fg_color="#f5f5f5")  # Light gray background
        self.main_container.pack(expand=True, fill="both")

        # Create sidebar with darker accent
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=200,
            corner_radius=0,
            fg_color="#2d5a9e"  # Dark blue sidebar
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Dashboard title in sidebar
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Admin Dashboard",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(pady=20)

        # Navigation buttons
        self.nav_buttons = []
        tabs = ["Trainers", "Batches", "Trainees", "Exams", "Results"]
        
        for tab in tabs:
            btn = ctk.CTkButton(
                self.sidebar,
                text=tab,
                command=lambda t=tab: self.change_tab(t),
                width=180,
                height=40,
                corner_radius=0,
                fg_color="transparent",
                text_color="white",
                hover_color=("gray70", "gray30")
            )
            btn.pack(pady=5)
            self.nav_buttons.append(btn)

        # Logout button at bottom of sidebar
        logout_button = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            command=self.logout,
            width=180,
            height=40
        )
        logout_button.pack(side="bottom", pady=20)

        # Main content area
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#ffffff"  # White background
        )
        self.content_frame.pack(side="left", expand=True, fill="both", padx=20, pady=20)

        # Initialize with first tab
        self.change_tab("Trainers")

    def change_tab(self, tab_name):
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update current tab
        self.current_tab = tab_name.lower()
        self.selected_record_id = None
        
        print("Current Tab:" + self.current_tab)

        # Update nav button states
        for btn in self.nav_buttons:
            if btn.cget("text") == tab_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        # Create new tab content
        self.create_tab_content(self.content_frame, self.current_tab)
        
        # Refresh table data immediately after creation
        self.refresh_table()

    def create_tab_content(self, tab, tab_type):
        # Main container frame
        container = ctk.CTkFrame(tab)
        container.pack(expand=True, fill="both", padx=10, pady=10)

        # Top action bar
        action_bar = ctk.CTkFrame(container)
        action_bar.pack(fill="x", padx=5, pady=(0, 10))

        # Title for the section
        section_title = ctk.CTkLabel(
            action_bar,
            text=f"{tab_type.title()} Management",
            font=("Helvetica", 16, "bold")
        )
        section_title.pack(side="left", padx=5)

        # CRUD Buttons frame
        buttons_frame = ctk.CTkFrame(action_bar, fg_color="transparent")
        buttons_frame.pack(side="right", padx=5)

        # Add CRUD buttons
        if tab_type == "exams":
            buttons = [
                ("Add Exam", lambda: self.open_exam_details_modal("add")),
                ("Edit Details", lambda: self.open_exam_details_modal("update")),
                ("Manage Questions", self.open_questions_modal),
                ("Delete", self.delete_record)
            ]
        else:
            buttons = [
                ("Add", self.add_record),
                ("Update", self.update_record),
                ("Delete", self.delete_record)
            ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                width=120,
                height=32,
                fg_color=BUTTON_COLORS["primary"][0],
                hover_color=BUTTON_COLORS["primary"][1],
                text_color="white"
            )
            btn.pack(side="left", padx=5)

        # Table frame
        table_frame = ctk.CTkFrame(container)
        table_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # Create table with custom style
        style = ttk.Style()
        
        # Configure the custom style for the table
        style.configure(
            "Custom.Treeview",
            background="#ffffff",      # White background
            foreground="#1a1a1a",     # Dark text
            fieldbackground="#ffffff",
            rowheight=30,             # Increased row height
            borderwidth=0,            # Remove border
            font=('Helvetica', 10)
        )
        
        # Configure the headers
        style.configure(
            "Custom.Treeview.Heading",
            background="#f0f0f0",     # Light gray header background
            foreground="#1a1a1a",     # Black text for headers
            relief="flat",
            font=('Helvetica', 10, 'bold'),
            borderwidth=0,
            padding=5                 # Add padding to headers
        )
        
        # Configure selection colors and alternating rows
        style.map(
            "Custom.Treeview",
            background=[
                ("selected", "#e6f3ff"),    # Light blue selection
                ("!selected", "#ffffff"),    # White background
                ("alternate", "#fafafa")     # Very light gray alternating rows
            ],
            foreground=[
                ("selected", "#1a1a1a"),    # Keep text dark even when selected
                ("!selected", "#1a1a1a")
            ]
        )

        # Configure the scrollbar style
        style.configure(
            "Custom.Vertical.TScrollbar",
            background="#ffffff",
            troughcolor="#f0f0f0",
            bordercolor="#e0e0e0",
            arrowcolor="#666666",     # Darker arrows
            width=12                  # Slightly wider scrollbar
        )

        columns = self.get_columns(tab_type)
        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview"
        )

        # Configure columns with better spacing
        for col in columns:
            table.heading(
                col, 
                text=col.replace('_', ' ').title(),
                anchor="w"            # Left-align headers
            )
            table.column(
                col, 
                width=100,
                minwidth=50,
                anchor="w"            # Left-align content
            )

        # Add a subtle border to the table frame
        table_frame.configure(
            border_width=1,
            border_color="#e0e0e0",
            corner_radius=6
        )

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=table.yview,
            style="Custom.Vertical.TScrollbar"
        )
        x_scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=table.xview,
            style="Custom.Vertical.TScrollbar"
        )
        table.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)

        # Pack table and scrollbars
        table.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        table.bind('<ButtonRelease-1>', self.on_table_select)
        setattr(self, f"{tab_type}_table", table)

    def on_table_select(self, event):
        table = getattr(self, f"{self.current_tab}_table")
        selected_item = table.selection()
        if not selected_item:
            return
        values = table.item(selected_item[0])['values']
        self.selected_record_id = values[0]
        print(f"Selected Record ID: {self.selected_record_id}")
        
        # If in exams tab, show the exam details
        if self.current_tab == "exams":
            self.open_exam_details_modal(mode="update")

    def refresh_table(self):
        table = getattr(self, f"{self.current_tab}_table")
        table.delete(*table.get_children())
        records = self.db_manager.get_all_records(self.current_tab)
        for record in records:
            table.insert('', 'end', values=record)

    def open_exam_details_modal(self, mode="add"):
        modal = BaseModal(
            self.master,
            f"{mode.capitalize()} Exam Details",
            "400x500"
        )

        # Create form frame
        form_frame = ctk.CTkFrame(modal.container, fg_color="transparent")
        form_frame.pack(expand=True, fill="both")

        # Input fields
        fields = ["title", "module_no", "num_items", "time_limit", "batch_id"]
        input_fields = {}

        for field in fields:
            field_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)

            label = ctk.CTkLabel(
                field_frame,
                text=field.replace('_', ' ').title() + ":",
                width=100
            )
            label.pack(side="left", padx=5)

            entry = ctk.CTkEntry(
                field_frame,
                placeholder_text=f"Enter {field.replace('_', ' ')}...",
                fg_color="#ffffff",
                border_color="#2d5a9e",
                border_width=1,
                text_color="#1a1a1a",
                placeholder_text_color="#999999"
            )
            entry.pack(side="left", expand=True, fill="x", padx=5)
            input_fields[field] = entry

        # Populate fields if updating
        if mode == "update" and self.selected_record_id:
            record = self.db_manager.get_record_by_id('exams', self.selected_record_id)
            print(f"RECORD: {record}")
            if record:
                columns = ['id', 'title', 'module_no', 'num_items', 'time_limit', 'batch_id', 'created_at', 'status']
                record_dict = dict(zip(columns, record))
                print(f"Columns: {columns}")
                print(f"Record_dict: {record_dict}")
                # Update each field with its corresponding value
                for field in fields:
                    if field in record_dict and record_dict[field] is not None:
                        input_fields[field].delete(0, 'end')
                        input_fields[field].insert(0, str(record_dict[field]))
                            

        def save():
            try:
                data = {field: entry.get().strip() 
                       for field, entry in input_fields.items()}
                print(f"Saved Data: {data}")
                
                if mode == "add":
                    self.db_manager.insert_record('exams', data)
                else:
                    self.db_manager.update_record('exams', self.selected_record_id, data)
                
                modal.destroy()
                self.refresh_table()
                messagebox.showinfo("Success", f"Exam details {mode}d successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Create buttons
        modal.create_button_group([
            ("Save", save, ("#1f538d", "#164279")),
            ("Cancel", modal.destroy, ("gray", "darkgray"))
        ])

    def open_questions_modal(self):
        if not self.selected_record_id:
            messagebox.showerror("Error", "Please select an exam first")
            return

        modal = BaseModal(
            self.master,
            "Manage Exam Questions",
            "800x600"
        )

        # Questions list frame with custom styling
        questions_frame = ctk.CTkScrollableFrame(
            modal.container,
            fg_color="#333333",
            corner_radius=6
        )
        questions_frame.pack(expand=True, fill="both", pady=(0, 10))

        questions_list = []

        def add_question(question_data=None):
            question_frame = ctk.CTkFrame(
                questions_frame,
                fg_color="#ffffff",
                corner_radius=6,
                border_width=1,
                border_color="#e0e0e0"
            )
            question_frame.pack(fill="x", padx=5, pady=5)

            # Question number
            q_num = len(questions_list) + 1
            q_label = ctk.CTkLabel(
                question_frame,
                text=f"Question {q_num}",
                font=("Helvetica", 12, "bold"),
                text_color="#1a1a1a"
            )
            q_label.pack(pady=5)

            # Question text
            q_text = ctk.CTkTextbox(
                question_frame,
                height=60,
                fg_color="#ffffff",
                border_color="#2d5a9e",
                border_width=1,
                text_color="#1a1a1a"
            )
            q_text.pack(fill="x", padx=5, pady=5)

            # Options frame
            options_frame = ctk.CTkFrame(question_frame, fg_color="transparent")
            options_frame.pack(fill="x", padx=5)

            options = []
            for i in range(4):
                option_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
                option_frame.pack(fill="x", pady=2)
                
                option_label = ctk.CTkLabel(
                    option_frame,
                    text=f"Option {chr(65+i)}:",
                    width=70,
                    text_color="#1a1a1a"
                )
                option_label.pack(side="left", padx=5)
                
                option_entry = ctk.CTkEntry(
                    option_frame,
                    fg_color="#ffffff",
                    border_color="#2d5a9e",
                    border_width=1,
                    text_color="#1a1a1a"
                )
                option_entry.pack(side="left", expand=True, fill="x", padx=5)
                
                options.append(option_entry)

            # Correct answer and points frame
            settings_frame = ctk.CTkFrame(question_frame, fg_color="transparent")
            settings_frame.pack(fill="x", padx=5, pady=5)

            # Correct answer dropdown
            correct_label = ctk.CTkLabel(settings_frame, text="Correct Answer:")
            correct_label.pack(side="left", padx=5)
            
            correct_var = tk.StringVar(value="A")
            correct_menu = ctk.CTkOptionMenu(
                settings_frame,
                values=["A", "B", "C", "D"],
                variable=correct_var,
                fg_color="#ffffff",
                text_color="#1a1a1a"
            )
            correct_menu.pack(side="left", padx=5)

            # Points entry
            points_label = ctk.CTkLabel(settings_frame, text="Points:")
            points_label.pack(side="left", padx=5)
            
            points_entry = ctk.CTkEntry(settings_frame, width=50, fg_color="#ffffff", text_color="#1a1a1a")
            points_entry.insert(0, "1")
            points_entry.pack(side="left", padx=5)

            # Delete button
            delete_btn = ctk.CTkButton(
                question_frame,
                text="Delete Question",
                command=lambda: remove_question(question_frame),
                fg_color=BUTTON_COLORS["danger"][0],
                hover_color=BUTTON_COLORS["danger"][1],
                text_color="white"
            )
            delete_btn.pack(pady=5)

            question_dict = {
                'frame': question_frame,
                'text': q_text,
                'options': options,
                'correct': correct_var,
                'points': points_entry,
                'id': question_data['id'] if question_data else None
            }
            questions_list.append(question_dict)

            # If question_data provided, populate fields
            if question_data:
                q_text.insert('1.0', question_data['question_text'])
                options_data = question_data['correct_answer'].split('|')
                for i, option in enumerate(options_data):
                    answer, text = option.split(':')
                    options[i].insert(0, text)
                    if answer.startswith('*'):
                        correct_var.set(answer[1])
                points_entry.delete(0, 'end')
                points_entry.insert(0, str(question_data['points']))

        def remove_question(frame):
            question_dict = next(q for q in questions_list if q['frame'] == frame)
            if question_dict['id']:  # If question exists in database
                self.db_manager.delete_record('questions', question_dict['id'])
            frame.destroy()
            questions_list.remove(question_dict)
            # Renumber remaining questions
            for i, q in enumerate(questions_list, 1):
                q['frame'].winfo_children()[0].configure(text=f"Question {i}")

        # Load existing questions
        existing_questions = self.db_manager.get_exam_questions(self.selected_record_id)
        for question in existing_questions:
            add_question({
                'id': question[0],
                'question_text': question[1],
                'correct_answer': question[2],
                'points': question[3]
            })

        # Add question button
        add_button = ctk.CTkButton(
            modal.container,
            text="Add New Question",
            command=lambda: add_question()
        )
        add_button.pack(pady=10)

        def save_questions():
            try:
                for q in questions_list:
                    question_text = q['text'].get('1.0', 'end-1c').strip()
                    options = []
                    correct_letter = q['correct'].get()
                    
                    for i, opt in enumerate(q['options']):
                        letter = chr(65 + i)
                        prefix = '*' if letter == correct_letter else ''
                        options.append(f"{prefix}{letter}:{opt.get().strip()}")

                    question_data = {
                        'exam_id': self.selected_record_id,
                        'question_text': question_text,
                        'correct_answer': '|'.join(options),
                        'points': int(q['points'].get()),
                        'question_type': 'multiple_choice'
                    }

                    if q['id']:  # Update existing question
                        self.db_manager.update_record('questions', q['id'], question_data)
                    else:  # Insert new question
                        self.db_manager.insert_record('questions', question_data)

                messagebox.showinfo("Success", "Questions saved successfully!")
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Save button
        save_button = ctk.CTkButton(
            modal.container,
            text="Save All Questions",
            command=save_questions
        )
        save_button.pack(pady=10)

    def open_modal(self, mode="add"):
        if self.current_tab == "exams":
            self.open_exam_details_modal(mode, self.selected_record_id if mode == "update" else None)
            return

        modal = BaseModal(
            self.master,
            f"{mode.capitalize()} {self.current_tab.title()}",
            "500x600"
        )

        # Create scrollable form frame
        form_frame = ctk.CTkScrollableFrame(
            modal.container,
            fg_color="transparent"
        )
        form_frame.pack(expand=True, fill="both", padx=5, pady=5)

        input_fields = {}
        fields = self.get_fields(self.current_tab)

        for field in fields:
            if field == 'id':  # Skip ID field
                continue
            
            field_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)  # Increased spacing between fields

            label = ctk.CTkLabel(
                field_frame,
                text=field.replace('_', ' ').title() + ":",
                width=120,
                anchor="e",          # Right-align labels
                text_color="#1a1a1a"
            )
            label.pack(side="left", padx=5)

            if field in ['hire_date', 'date_taken']:
                # Date field with hint
                entry_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
                entry_frame.pack(side="left", expand=True, fill="x")
                
                entry = ctk.CTkEntry(
                    entry_frame,
                    placeholder_text="YYYY-MM-DD",
                    fg_color="#ffffff",
                    border_color="#2d5a9e",
                    border_width=1,
                    text_color="#1a1a1a",
                    placeholder_text_color="#999999",
                    height=32
                )
                entry.pack(fill="x", padx=5)
                entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
                
                hint_label = ctk.CTkLabel(
                    entry_frame,
                    text="Format: YYYY-MM-DD",
                    font=("Helvetica", 8),
                    text_color="gray70"
                )
                hint_label.pack(pady=(0, 5))
            else:
                entry = ctk.CTkEntry(
                    field_frame,
                    placeholder_text=f"Enter {field.replace('_', ' ')}...",
                    fg_color="#ffffff",
                    border_color="#2d5a9e",
                    border_width=1,
                    text_color="#1a1a1a",
                    placeholder_text_color="#999999",
                    height=32
                )
                entry.pack(side="left", expand=True, fill="x", padx=5)
            
            input_fields[field] = entry

        # Populate fields if updating
        if mode == "update":
            record = self.db_manager.get_record_by_id(self.current_tab, self.selected_record_id)
            if record:
                for idx, col in enumerate(fields):
                    if col != 'id':
                        value = record[fields.index(col)]
                        if value is not None:
                            input_fields[col].delete(0, tk.END)
                            input_fields[col].insert(0, str(value))

        def save():
            try:
                data = {key: entry.get().strip() for key, entry in input_fields.items()}
                
                # Validate required fields
                empty_fields = [k for k, v in data.items() if not v]
                if empty_fields:
                    raise ValueError(f"Please fill in all required fields: {', '.join(empty_fields)}")
                
                if mode == "add":
                    self.db_manager.insert_record(self.current_tab, data)
                    messagebox.showinfo("Success", "Record added successfully!")
                else:
                    self.db_manager.update_record(self.current_tab, self.selected_record_id, data)
                    messagebox.showinfo("Success", "Record updated successfully!")
                
                modal.destroy()
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Create buttons with consistent styling
        modal.create_button_group([
            ("Save", save, BUTTON_COLORS["primary"]),
            ("Cancel", modal.destroy, BUTTON_COLORS["secondary"])
        ])

    def add_record(self):
        self.open_modal(mode="add")

    def update_record(self):
        if not self.selected_record_id:
            messagebox.showerror("Error", "Please select a record to update")
            return
        self.open_modal(mode="update")

    def delete_record(self):
        if not self.selected_record_id:
            messagebox.showerror("Error", "Please select a record to delete")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            self.db_manager.delete_record(self.current_tab, self.selected_record_id)
            messagebox.showinfo("Success", "Record deleted successfully!")
            self.refresh_table()

    def get_columns(self, tab_type):
        columns_map = {
            "trainers": ["id", "name", "class_assigned", "contact_email", "hire_date"],
            "batches": ["id", "batch_year", "num_trainees", "training_duration", "training_location", "trainer_id"],
            "trainees": ["id", "name", "id_no", "uli", "batch_year", "trainer_name", "exams_taken", "status", "remarks", "batch_id"],
            "exams": ["id", "title", "module_no", "num_items", "time_limit", "batch_id"],
            "results": ["id", "trainee_id", "trainer_id", "exam_id", "competency", "date_taken", "remarks"]
        }
        return columns_map.get(tab_type, [])

    def get_fields(self, tab_type):
        return self.get_columns(tab_type)[0:]

    def logout(self):
        self.main_container.destroy()
        self.logout_callback()

    def create_results_tab(self, tab):
        # Create modern table for results
        columns = [
            "Trainee", "Exam", "Score", "Percentage",
            "Date Taken", "Time Spent", "Status"
        ]
        
        self.results_table = self.create_table(tab, columns)
        
        # Add filter controls
        filter_frame = ctk.CTkFrame(tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Add batch filter
        batch_filter = ctk.CTkComboBox(
            filter_frame,
            values=self.db_manager.get_batch_list(),
            command=self.filter_results
        )
        batch_filter.pack(side="left", padx=5)
        
        # Add export button
        export_btn = ctk.CTkButton(
            filter_frame,
            text="Export Results",
            command=self.export_results
        )
        export_btn.pack(side="right", padx=5)

    def filter_results(self, batch_id=None):
        results = self.db_manager.get_results(batch_id)
        self.populate_results_table(results)
