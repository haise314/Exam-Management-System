import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3

class AdminDashboard:
    def __init__(self, master, db_manager, logout_callback):
        self.master = master
        self.db_manager = db_manager
        self.logout_callback = logout_callback
        self.current_tab = "trainers"
        self.selected_record_id = None

        # Create main container
        self.main_container = ctk.CTkFrame(master)
        self.main_container.pack(expand=True, fill="both")

        # Create sidebar
        self.sidebar = ctk.CTkFrame(
            self.main_container,
            width=200,
            corner_radius=0
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
        self.content_frame = ctk.CTkFrame(self.main_container)
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

        # Update nav button states
        for btn in self.nav_buttons:
            if btn.cget("text") == tab_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        # Create new tab content
        self.create_tab_content(self.content_frame, self.current_tab)

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
                height=32
            )
            btn.pack(side="left", padx=5)

        # Table frame
        table_frame = ctk.CTkFrame(container)
        table_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # Create table with custom style
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=25
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#1f538d",
            foreground="white",
            relief="flat"
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")]
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
            table.heading(col, text=col.replace('_', ' ').title())
            table.column(col, width=100)

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
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
        
        # If in exams tab, show the exam details
        if self.current_tab == "exams":
            self.open_exam_modal(mode="update", exam_id=self.selected_record_id)

    def refresh_table(self):
        table = getattr(self, f"{self.current_tab}_table")
        table.delete(*table.get_children())
        records = self.db_manager.get_all_records(self.current_tab)
        for record in records:
            table.insert('', 'end', values=record)

    def open_exam_details_modal(self, mode="add"):
        modal = ctk.CTkToplevel(self.master)
        modal.title(f"{mode.capitalize()} Exam Details")
        modal.geometry("400x500")

        # Create form frame
        form_frame = ctk.CTkFrame(modal)
        form_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            form_frame,
            text=f"{mode.capitalize()} Exam Details",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

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

            entry = ctk.CTkEntry(field_frame)
            entry.pack(side="left", expand=True, fill="x", padx=5)
            input_fields[field] = entry

        # Populate fields if updating
        if mode == "update" and self.selected_record_id:
            record = self.db_manager.get_record_by_id('exams', self.selected_record_id)
            if record:
                # Map record values to fields
                field_values = dict(zip(fields, record[1:]))  # Skip ID
                for field, value in field_values.items():
                    if value is not None:
                        input_fields[field].insert(0, str(value))

        def save():
            try:
                data = {field: entry.get().strip() 
                       for field, entry in input_fields.items()}
                
                if mode == "add":
                    self.db_manager.insert_record('exams', data)
                else:
                    self.db_manager.update_record('exams', self.selected_record_id, data)
                
                modal.destroy()
                self.refresh_table()
                messagebox.showinfo("Success", f"Exam details {mode}d successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=save,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=modal.destroy,
            width=100
        ).pack(side="left", padx=5)

    def open_questions_modal(self):
        if not self.selected_record_id:
            messagebox.showerror("Error", "Please select an exam first")
            return

        modal = ctk.CTkToplevel(self.master)
        modal.title("Manage Exam Questions")
        modal.geometry("800x600")

        # Main container
        container = ctk.CTkFrame(modal)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Questions list frame
        questions_frame = ctk.CTkScrollableFrame(container)
        questions_frame.pack(expand=True, fill="both", pady=(0, 10))

        questions_list = []

        def add_question(question_data=None):
            question_frame = ctk.CTkFrame(questions_frame)
            question_frame.pack(fill="x", padx=5, pady=5)

            # Question number
            q_num = len(questions_list) + 1
            q_label = ctk.CTkLabel(
                question_frame,
                text=f"Question {q_num}",
                font=("Helvetica", 12, "bold")
            )
            q_label.pack(pady=5)

            # Question text
            q_text = ctk.CTkTextbox(question_frame, height=60)
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
                    width=70
                )
                option_label.pack(side="left", padx=5)
                
                option_entry = ctk.CTkEntry(option_frame)
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
                variable=correct_var
            )
            correct_menu.pack(side="left", padx=5)

            # Points entry
            points_label = ctk.CTkLabel(settings_frame, text="Points:")
            points_label.pack(side="left", padx=5)
            
            points_entry = ctk.CTkEntry(settings_frame, width=50)
            points_entry.insert(0, "1")
            points_entry.pack(side="left", padx=5)

            # Delete button
            delete_btn = ctk.CTkButton(
                question_frame,
                text="Delete Question",
                command=lambda: remove_question(question_frame),
                fg_color="red",
                hover_color="darkred"
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
            container,
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
            container,
            text="Save All Questions",
            command=save_questions
        )
        save_button.pack(pady=10)

    def open_modal(self, mode="add"):
        if self.current_tab == "exams":
            self.open_exam_modal(mode, self.selected_record_id if mode == "update" else None)
        else:
            # Original modal code for other tabs
            modal = tk.Toplevel(self.master)
            modal.title(f"{mode.capitalize()} {self.current_tab.title()}")
            modal.geometry("400x400")

            # Create a canvas with scrollbar for many fields
            canvas = tk.Canvas(modal)
            scrollbar = tk.Scrollbar(modal, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            input_fields = {}
            fields = self.get_fields(self.current_tab)

            for idx, label in enumerate(fields):
                if label == 'id':  # Skip ID field for add/update
                    continue
                
                lbl = tk.Label(scrollable_frame, text=label.replace("_", " ").title())
                lbl.pack(pady=5)

                # Special handling for date fields
                if label in ['hire_date', 'date_taken']:
                    entry = tk.Entry(scrollable_frame)
                    entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
                    entry.pack(pady=5)
                    hint_label = tk.Label(scrollable_frame, text="Format: YYYY-MM-DD", font=("Helvetica", 8))
                    hint_label.pack()
                else:
                    entry = tk.Entry(scrollable_frame)
                    entry.pack(pady=5)
                
                input_fields[label] = entry

            if mode == "update":
                record = self.db_manager.get_record_by_id(self.current_tab, self.selected_record_id)
                if record:
                    # Skip the ID field when populating
                    for idx, col in enumerate(fields):
                        if col != 'id':  # Skip ID field
                            value = record[fields.index(col)]
                            if value is not None:  # Only set value if not None
                                input_fields[col].delete(0, tk.END)
                                input_fields[col].insert(0, str(value))

            def save():
                data = {key: entry.get().strip() for key, entry in input_fields.items()}
                try:
                    if mode == "add":
                        self.db_manager.insert_record(self.current_tab, data)
                        messagebox.showinfo("Success", "Record added successfully!")
                    elif mode == "update":
                        self.db_manager.update_record(self.current_tab, self.selected_record_id, data)
                        messagebox.showinfo("Success", "Record updated successfully!")
                    modal.destroy()
                    self.refresh_table()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Database error: {str(e)}")

            save_btn = tk.Button(scrollable_frame, text="Save", command=save)
            save_btn.pack(pady=20)

            # Pack the canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y")

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
