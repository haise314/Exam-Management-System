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

        # Create main admin dashboard frame
        self.admin_frame = ctk.CTkFrame(master)
        self.admin_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Dashboard title
        title_label = ctk.CTkLabel(
            self.admin_frame, text="Admin Dashboard", font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(20, 10))

        # Create tabs
        self.tabview = ctk.CTkTabview(self.admin_frame)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        # Add tabs
        tabs = ["Trainers", "Batches", "Trainees", "Exams", "Results"]
        for tab_name in tabs:
            tab = self.tabview.add(tab_name)
            self.create_tab_content(tab, tab_name.lower())

        # Set initial tab
        self.tabview.set("Trainers")
        
        # Use tabview's set method to track tab changes
        self.tabview.configure(command=self.on_tab_changed)

        # CRUD Buttons
        crud_frame = ctk.CTkFrame(self.admin_frame)
        crud_frame.pack(pady=10)

        buttons = [
            ("Add", self.add_record),
            ("Update", self.update_record),
            ("Delete", self.delete_record)
        ]

        for text, command in buttons:
            button = ctk.CTkButton(crud_frame, text=text, command=command)
            button.pack(side=tk.LEFT, padx=5)

        # Logout button
        logout_button = ctk.CTkButton(self.admin_frame, text="Logout", command=self.logout)
        logout_button.pack(pady=10)

        self.refresh_table()

    def on_tab_changed(self, new_tab=None):
        # If no new_tab is provided, get the current tab
        if new_tab is None:
            new_tab = self.tabview.get()
        
        # Convert to lowercase for consistency
        self.current_tab = new_tab.lower()
        print(f"Current tab: {self.current_tab}")
        self.selected_record_id = None
        self.refresh_table()

    def create_tab_content(self, tab, tab_type):
        frame = ctk.CTkFrame(tab)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        columns = self.get_columns(tab_type)
        table = ttk.Treeview(frame, columns=columns, show='headings')

        for col in columns:
            table.heading(col, text=col.replace('_', ' ').title())
            table.column(col, width=100)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscroll=scrollbar.set)

        table.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        table.bind('<ButtonRelease-1>', self.on_table_select)
        setattr(self, f"{tab_type}_table", table)
        self.refresh_table()

    def on_table_select(self, event):
        table = getattr(self, f"{self.current_tab}_table")
        selected_item = table.selection()
        if not selected_item:
            return
        values = table.item(selected_item[0])['values']
        print(f"Selected item: {values}")
        self.selected_record_id = values[0]

    def refresh_table(self):
        table = getattr(self, f"{self.current_tab}_table")
        table.delete(*table.get_children())
        records = self.db_manager.get_all_records(self.current_tab)
        for record in records:
            table.insert('', 'end', values=record)

    def open_modal(self, mode="add"):
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
        self.admin_frame.destroy()
        self.logout_callback()
