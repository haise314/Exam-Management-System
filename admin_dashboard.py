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

    @staticmethod
    def center_window(window, default_width=None, default_height=None):
        window.update_idletasks()  # Ensure the window size is updated
        width = default_width or window.winfo_width()
        height = default_height or window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x}+{y}")    
    
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

        # Configure columns
        for col in columns:
            table.heading(col, text=col.replace('_', ' ').title(), anchor="w")
            table.column(col, width=100, minwidth=50, anchor="w")

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

        table.bind('<Double-1>', self.on_table_select)
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

        # Ensure column order matches the database schema
        column_order = self.get_columns(self.current_tab)
        for record in records:
            # Reorder record fields to match column order
            reordered_record = [record[column_order.index(col)] for col in column_order]
            table.insert('', 'end', values=reordered_record)

    def open_exam_details_modal(self, mode="add"):
        modal = BaseModal(
            self.master,
            f"{mode.capitalize()} Exam Details",
            "500x550"  # Slightly larger size
        )

        # Create main container frame
        main_container = ctk.CTkFrame(modal.scrollable_frame, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Create header section with icon or image if in update mode
        if mode == "update":
            header = ctk.CTkFrame(
                main_container,
                fg_color="#f0f5ff",  # Light blue background
                corner_radius=8,
                border_width=1,
                border_color="#d0d9e8"
            )
            header.pack(fill="x", pady=(0, 15))
            
            header_text = ctk.CTkLabel(
                header,
                text="Edit Exam Information",
                font=("Helvetica", 14, "bold"),
                text_color="#2d5a9e"
            )
            header_text.pack(pady=10)

        # Create form frame with better styling
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Define input fields with better labels and structure
        fields = [
            {"name": "title", "label": "Exam Title", "placeholder": "Enter the exam title..."},
            {"name": "module_no", "label": "Module Number", "placeholder": "Enter module number..."},
            {"name": "num_items", "label": "Number of Items", "placeholder": "Enter total question count..."},
            {"name": "time_limit", "label": "Time Limit (minutes)", "placeholder": "Enter exam time limit..."},
            {"name": "batch_id", "label": "Batch ID", "placeholder": "Enter batch ID..."}
        ]
        
        input_fields = {}

        for field in fields:
            # Create field container
            field_container = ctk.CTkFrame(form_frame, fg_color="transparent")
            field_container.pack(fill="x", pady=10)
            
            # Add label with better styling
            label = ctk.CTkLabel(
                field_container,
                text=field["label"],
                font=("Helvetica", 12, "bold"),
                text_color="#333333"
            )
            label.pack(anchor="w", padx=5, pady=(0, 5))
            
            # Add input with better styling
            entry = ctk.CTkEntry(
                field_container,
                placeholder_text=field["placeholder"],
                height=35,
                fg_color="#ffffff",
                border_color="#c0c0c0",
                border_width=1,
                text_color="#333333",
                corner_radius=4
            )
            entry.pack(fill="x", padx=5)
            
            # Store reference
            input_fields[field["name"]] = entry

        # Add a status toggle if in update mode
        status_var = tk.StringVar(value="active")
        
        if mode == "update":
            status_container = ctk.CTkFrame(form_frame, fg_color="transparent")
            status_container.pack(fill="x", pady=10)
            
            status_label = ctk.CTkLabel(
                status_container,
                text="Exam Status",
                font=("Helvetica", 12, "bold"),
                text_color="#333333"
            )
            status_label.pack(anchor="w", padx=5, pady=(0, 5))
            
            status_frame = ctk.CTkFrame(status_container, fg_color="transparent")
            status_frame.pack(fill="x", padx=5)
            
            active_radio = ctk.CTkRadioButton(
                status_frame,
                text="Active",
                variable=status_var,
                value="active",
                fg_color="#2d5a9e",
                font=("Helvetica", 11)
            )
            active_radio.pack(side="left", padx=(0, 20))
            
            inactive_radio = ctk.CTkRadioButton(
                status_frame,
                text="Inactive",
                variable=status_var,
                value="inactive",
                fg_color="#2d5a9e",
                font=("Helvetica", 11)
            )
            inactive_radio.pack(side="left")

        # Populate fields if updating
        if mode == "update" and self.selected_record_id:
            record = self.db_manager.get_record_by_id('exams', self.selected_record_id)
            if record:
                columns = ['id', 'title', 'module_no', 'num_items', 'time_limit', 'batch_id', 'created_at', 'status']
                record_dict = dict(zip(columns, record))
                
                # Update each field with its corresponding value
                for field_name, entry in input_fields.items():
                    if field_name in record_dict and record_dict[field_name] is not None:
                        entry.delete(0, 'end')
                        entry.insert(0, str(record_dict[field_name]))
                
                # Set status if available
                if 'status' in record_dict and record_dict['status']:
                    status_var.set(record_dict['status'])

        # Action button container
        action_container = ctk.CTkFrame(main_container, fg_color="transparent")
        action_container.pack(fill="x", pady=15)

        def save():
            try:
                # Validate inputs
                for field_name, entry in input_fields.items():
                    if not entry.get().strip():
                        messagebox.showerror("Error", f"{field_name.replace('_', ' ').title()} cannot be empty")
                        return
                
                data = {field_name: entry.get().strip() 
                       for field_name, entry in input_fields.items()}
                
                # Add status if in update mode
                if mode == "update":
                    data['status'] = status_var.get()
                
                if mode == "add":
                    self.db_manager.insert_record('exams', data)
                    result_message = "Exam created successfully!"
                else:
                    self.db_manager.update_record('exams', self.selected_record_id, data)
                    result_message = "Exam updated successfully!"
                
                modal.destroy()
                self.refresh_table()
                
                messagebox.showinfo("Success", result_message)
                
                # If creating a new exam, offer to add questions
                if mode == "add" and messagebox.askyesno("Add Questions", "Would you like to add questions to this exam now?"):
                    # Get the id of the newly created exam
                    exams = self.db_manager.get_all_records('exams')
                    for exam in exams:
                        if exam[1] == data['title']:  # Match by title
                            self.selected_record_id = exam[0]
                            self.open_questions_modal()
                            break
                    
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Create action buttons
        save_btn = ctk.CTkButton(
            action_container,
            text="Save Exam",
            command=save,
            fg_color="#2d5a9e",
            hover_color="#1f4682",
            height=36,
            font=("Helvetica", 13, "bold")
        )
        save_btn.pack(side="right", padx=5)
        
        cancel_btn = ctk.CTkButton(
            action_container,
            text="Cancel",
            command=modal.destroy,
            fg_color="#9e9e9e",  # Gray for cancel
            hover_color="#757575",
            height=36,
            font=("Helvetica", 13)
        )
        cancel_btn.pack(side="right", padx=5)
        
        # If in update mode, add a button to manage questions
        if mode == "update":
            questions_btn = ctk.CTkButton(
                action_container,
                text="Manage Questions",
                command=self.open_questions_modal,
                fg_color="#ff9800",  # Orange for manage questions
                hover_color="#f57c00",
                height=36,
                font=("Helvetica", 13)
            )
            questions_btn.pack(side="left", padx=5)

    def open_questions_modal(self):
        if not self.selected_record_id:
            messagebox.showerror("Error", "Please select an exam first")
            return

        # Get exam details for title
        exam_details = self.db_manager.get_record_by_id('exams', self.selected_record_id)
        exam_title = exam_details[1] if exam_details else "Unknown Exam"

        modal = BaseModal(
            self.master,
            f"Manage Questions: {exam_title}",
            "900x700"  # Increased size for better visibility
        )

        # Main container with better spacing
        main_container = ctk.CTkFrame(modal.scrollable_frame, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Create info panel at the top
        info_panel = ctk.CTkFrame(
            main_container,
            fg_color="#f0f5ff",  # Light blue background
            corner_radius=8,
            border_width=1,
            border_color="#d0d9e8"
        )
        info_panel.pack(fill="x", padx=5, pady=(0, 15))
        
        # Add exam info in the panel
        if exam_details:
            exam_info_text = f"Module {exam_details[2]} • {exam_details[3]} Items • {exam_details[4]} Minutes"
            
            info_title = ctk.CTkLabel(
                info_panel,
                text=exam_title,
                font=("Helvetica", 16, "bold"),
                text_color="#1a1a1a"
            )
            info_title.pack(anchor="w", padx=15, pady=(10, 5))
            
            info_details = ctk.CTkLabel(
                info_panel,
                text=exam_info_text,
                font=("Helvetica", 12),
                text_color="#555555"
            )
            info_details.pack(anchor="w", padx=15, pady=(0, 10))

        # Create toolbar with action buttons
        toolbar = ctk.CTkFrame(main_container, fg_color="transparent")
        toolbar.pack(fill="x", padx=5, pady=(0, 10))
        
        # Questions count display
        question_counter = ctk.CTkLabel(
            toolbar,
            text="0 Questions",
            font=("Helvetica", 12, "bold"),
            text_color="#555555"
        )
        question_counter.pack(side="left", padx=5)
        
        # Add question button
        add_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Question",
            font=("Helvetica", 12),
            fg_color="#2d5a9e",
            hover_color="#1f4682",
            height=32
        )
        add_btn.pack(side="right", padx=5)
        
        # Create scrollable container for questions
        questions_scroll = ctk.CTkScrollableFrame(
            main_container,
            fg_color="#ffffff",
            corner_radius=8,
            border_width=1,
            border_color="#e0e0e0"
        )
        questions_scroll.pack(expand=True, fill="both", padx=5, pady=(0, 15))
        
        # Questions list to track all questions
        questions_list = []
        
        # Function to update the question counter
        def update_counter():
            question_counter.configure(text=f"{len(questions_list)} Questions")
        
        def add_question(question_data=None):
            # Create question container with better styling
            q_container = ctk.CTkFrame(
                questions_scroll,
                fg_color="#f8f9fa",
                corner_radius=8,
                border_width=1,
                border_color="#e0e0e0"
            )
            q_container.pack(fill="x", padx=10, pady=8, anchor="n")
            
            # Question header with number and controls
            header = ctk.CTkFrame(q_container, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(10, 5))
            
            # Question number indicator
            q_num = len(questions_list) + 1
            q_label = ctk.CTkLabel(
                header,
                text=f"Question {q_num}",
                font=("Helvetica", 14, "bold"),
                text_color="#2d5a9e"
            )
            q_label.pack(side="left")
            
            # Controls
            controls = ctk.CTkFrame(header, fg_color="transparent")
            controls.pack(side="right")
            
            # Delete button
            delete_btn = ctk.CTkButton(
                controls,
                text="Delete",
                font=("Helvetica", 12),
                fg_color="#ff5252",
                hover_color="#e63939",
                width=80,
                height=28
            )
            delete_btn.pack(side="right", padx=5)
            
            # Question content frame
            content = ctk.CTkFrame(q_container, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=5)
            
            # Question text entry with label
            text_label = ctk.CTkLabel(
                content,
                text="Question Text:",
                font=("Helvetica", 12, "bold"),
                text_color="#333333"
            )
            text_label.pack(anchor="w", pady=(5, 0))
            
            q_text = ctk.CTkTextbox(
                content,
                height=70,
                fg_color="#ffffff",
                border_color="#c0c0c0",
                border_width=1,
                text_color="#333333",
                corner_radius=4
            )
            q_text.pack(fill="x", pady=5)
            
            # Options section
            options_label = ctk.CTkLabel(
                content,
                text="Answer Options:",
                font=("Helvetica", 12, "bold"),
                text_color="#333333"
            )
            options_label.pack(anchor="w", pady=(10, 5))
            
            # Options container
            options_container = ctk.CTkFrame(content, fg_color="transparent")
            options_container.pack(fill="x", pady=5)
            
            # Create 2x2 grid for options
            options_grid = [ctk.CTkFrame(options_container, fg_color="transparent") for _ in range(2)]
            for i, row in enumerate(options_grid):
                row.pack(fill="x", pady=3)
            
            options = []
            option_frames = []
            
            for i in range(4):
                row_idx = i // 2
                frame = ctk.CTkFrame(
                    options_grid[row_idx],
                    fg_color="#ffffff",
                    corner_radius=6,
                    border_width=1,
                    border_color="#e0e0e0"
                )
                frame.pack(side="left" if i % 2 == 0 else "right", expand=True, fill="x", padx=5)
                option_frames.append(frame)
                
                option_header = ctk.CTkFrame(frame, fg_color="transparent")
                option_header.pack(fill="x", padx=8, pady=(8, 0))
                
                option_letter = ctk.CTkLabel(
                    option_header,
                    text=f"Option {chr(65+i)}",
                    font=("Helvetica", 12, "bold"),
                    text_color="#555555",
                    width=70
                )
                option_letter.pack(side="left")
                
                # Add radio button for correct answer
                correct_var = tk.StringVar(value="A" if i == 0 and not question_data else "")
                
                correct_radio = ctk.CTkRadioButton(
                    option_header,
                    text="Correct",
                    variable=correct_var,
                    value=chr(65+i),
                    font=("Helvetica", 11),
                    fg_color="#2d5a9e",
                    text_color="#333333"
                )
                correct_radio.pack(side="right", padx=8)
                
                option_entry = ctk.CTkEntry(
                    frame,
                    fg_color="#ffffff",
                    border_color="#e0e0e0",
                    border_width=1,
                    text_color="#333333",
                    placeholder_text=f"Enter option {chr(65+i)}..."
                )
                option_entry.pack(fill="x", padx=8, pady=(5, 8), ipady=3)
                
                options.append({
                    'entry': option_entry,
                    'radio': correct_radio,
                    'var': correct_var
                })
            
            # Points / additional settings row
            settings_row = ctk.CTkFrame(content, fg_color="transparent")
            settings_row.pack(fill="x", pady=(10, 5))
            
            points_label = ctk.CTkLabel(
                settings_row,
                text="Points:",
                font=("Helvetica", 12),
                text_color="#333333"
            )
            points_label.pack(side="left", padx=(0, 5))
            
            points_entry = ctk.CTkEntry(
                settings_row,
                width=60,
                fg_color="#ffffff",
                border_color="#c0c0c0",
                text_color="#333333"
            )
            points_entry.insert(0, "1")
            points_entry.pack(side="left")
            
            # Store question data
            question_dict = {
                'frame': q_container,
                'text': q_text,
                'options': options,
                'points': points_entry,
                'id': question_data['id'] if question_data else None,
                'number_label': q_label
            }
            questions_list.append(question_dict)
            
            # Update question counter
            update_counter()
            
            # Connect delete button action
            delete_btn.configure(command=lambda: remove_question(q_container))
            
            # If question data provided, populate fields
            if question_data:
                q_text.insert('1.0', question_data['question_text'])
                
                # Parse options data
                options_data = question_data['correct_answer'].split('|')
                for i, option_data in enumerate(options_data):
                    if i < len(options):
                        answer, text = option_data.split(':')
                        options[i]['entry'].insert(0, text)
                        if answer.startswith('*'):
                            options[i]['var'].set(answer[1])
                
                # Set points
                points_entry.delete(0, 'end')
                points_entry.insert(0, str(question_data['points']))
        
        def remove_question(frame):
            # Find and remove the question
            question_dict = next(q for q in questions_list if q['frame'] == frame)
            if question_dict['id']:  # If question exists in database
                self.db_manager.delete_record('questions', question_dict['id'])
            
            # Remove from UI
            frame.destroy()
            questions_list.remove(question_dict)
            
            # Renumber remaining questions
            for i, q in enumerate(questions_list, 1):
                q['number_label'].configure(text=f"Question {i}")
            
            # Update counter
            update_counter()
        
        # Connect add button
        add_btn.configure(command=lambda: add_question())
        
        # Load existing questions
        existing_questions = self.db_manager.get_exam_questions(self.selected_record_id)
        for question in existing_questions:
            add_question({
                'id': question[0],
                'question_text': question[1],
                'correct_answer': question[2],
                'points': question[3]
            })
        
        # If no questions, add one blank question to start
        if not questions_list:
            add_question()
        
        # Bottom action bar with save button
        action_bar = ctk.CTkFrame(main_container, fg_color="transparent")
        action_bar.pack(fill="x", pady=10)
        
        # Save all button
        save_all_btn = ctk.CTkButton(
            action_bar,
            text="Save All Questions",
            font=("Helvetica", 13, "bold"),
            fg_color="#2d7c32",  # Green color for save
            hover_color="#1b5e20",
            height=36
        )
        save_all_btn.pack(side="right", padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            action_bar,
            text="Cancel",
            font=("Helvetica", 13),
            fg_color="#9e9e9e",  # Gray for cancel
            hover_color="#757575",
            height=36
        )
        cancel_btn.pack(side="right", padx=5)
        
        def save_questions():
            try:
                for q in questions_list:
                    question_text = q['text'].get('1.0', 'end-1c').strip()
                    
                    # Validate question text
                    if not question_text:
                        messagebox.showerror("Error", "Question text cannot be empty")
                        return
                    
                    options = []
                    correct_letter = None
                    
                    # Find the correct answer
                    for i, opt in enumerate(q['options']):
                        letter = chr(65 + i)
                        if opt['var'].get() == letter:
                            correct_letter = letter
                    
                    # Validate that a correct answer is selected
                    if not correct_letter:
                        messagebox.showerror("Error", "Each question must have a correct answer selected")
                        return
                    
                    # Build options string
                    for i, opt in enumerate(q['options']):
                        letter = chr(65 + i)
                        option_text = opt['entry'].get().strip()
                        
                        # Validate option text
                        if not option_text:
                            messagebox.showerror("Error", f"Option {letter} cannot be empty")
                            return
                        
                        prefix = '*' if letter == correct_letter else ''
                        options.append(f"{prefix}{letter}:{option_text}")
                    
                    # Validate points
                    try:
                        points = int(q['points'].get())
                        if points <= 0:
                            messagebox.showerror("Error", "Points must be a positive number")
                            return
                    except:
                        messagebox.showerror("Error", "Points must be a valid number")
                        return
                    
                    question_data = {
                        'exam_id': self.selected_record_id,
                        'question_text': question_text,
                        'correct_answer': '|'.join(options),
                        'points': points,
                        'question_type': 'multiple_choice'
                    }
                    
                    if q['id']:  # Update existing question
                        self.db_manager.update_record('questions', q['id'], question_data)
                    else:  # Insert new question
                        self.db_manager.insert_record('questions', question_data)
                
                messagebox.showinfo("Success", f"{len(questions_list)} questions saved successfully!")
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        # Connect buttons
        save_all_btn.configure(command=save_questions)
        cancel_btn.configure(command=modal.destroy)

    def open_modal(self, mode="add"):
        modal = BaseModal(
            self.master,
            f"{mode.capitalize()} {self.current_tab.title()}",
            "500x600"  # Default size for generic modals
        )

        # Center the modal with default size
        AdminDashboard.center_window(modal, default_width=500, default_height=600)

        # Create scrollable form frame
        form_frame = ctk.CTkFrame(
            modal.scrollable_frame,  # Updated from modal.container
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
        # Ensure column names match the database schema
        columns_map = {
            "trainers": ["id", "name", "class_assigned", "contact_email", "hire_date"],
            "batches": ["id", "batch_year", "num_trainees", "training_duration", "training_location", "trainer_id"],
            "trainees": ["id", "name", "id_no", "uli", "batch_id", "batch_year", "exams_taken", "status", "remarks"],
            "exams": ["id", "title", "module_no", "num_items", "time_limit", "batch_id", "created_at", "status"],
            "results": ["id", "trainee_id", "exam_id", "score", "total_items", "time_spent", "date_taken", "status"]
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


