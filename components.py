import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from config import THEME

class BaseModal(ctk.CTkToplevel):
    def __init__(self, parent, title, size="600x700"):  # Increased default size
        super().__init__(parent)

        # Ensure modal stays on top
        self.transient(parent)
        self.grab_set()

        # Update modal styling
        self.title(title)
        self.geometry(size)
        self.configure(fg_color=THEME["colors"]["surface"])

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self, bg=THEME["colors"]["surface"], highlightthickness=0)
        self.canvas.pack(side="left", expand=True, fill="both", padx=20, pady=20)

        # Add a functional vertical scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame inside the canvas for content
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Add title to the modal
        self.title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=title,
            font=THEME["fonts"]["heading"],  # Use heading font for better visibility
            text_color=THEME["colors"]["text"]
        )
        self.title_label.pack(pady=(10, 20))  # Add padding for better spacing

    def create_button_group(self, buttons):
        # Create a button group at the bottom of the modal
        button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        for text, command, colors in buttons:
            ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=120,  # Increased button width for better usability
                fg_color=colors[0] if colors else THEME["colors"]["primary"],
                hover_color=colors[1] if colors else THEME["colors"]["primary_hover"],
                text_color="white"
            ).pack(side="left", padx=10)  # Add spacing between buttons