import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from config import THEME

class BaseModal(ctk.CTkToplevel):
    def __init__(self, parent, title, size="600x700"):
        super().__init__(parent)

        # Ensure modal stays on top
        self.transient(parent)
        self.grab_set()

        # Update modal styling
        self.title(title)
        self.geometry(size)
        self.configure(fg_color=THEME["colors"]["surface"])
        
        # Make the modal resizable
        self.resizable(True, True)
        self.minsize(400, 300)  # Set minimum size
        
        # Create main container frame
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid configuration for responsive layout
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Add title to the modal
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text=title,
            font=THEME["fonts"]["heading"],
            text_color=THEME["colors"]["text"]
        )
        self.title_label.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        # Create a frame to hold the canvas and scrollbar
        self.scroll_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.scroll_container.grid(row=1, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)
        self.scroll_container.grid_rowconfigure(0, weight=1)

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(
            self.scroll_container,
            bg=THEME["colors"]["surface"],
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Add a functional vertical scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.scroll_container,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas for content
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Create the canvas window
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            tags="self.scrollable_frame"
        )

        # Bind events for proper scrolling and resizing
        self.bind("<Configure>", self._on_configure)
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mouse wheel events
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind("<Destroy>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_configure(self, event):
        # Update the size of the canvas window when the modal is resized
        if event.widget == self:
            self.update_idletasks()
            self.canvas.configure(width=self.main_container.winfo_width())

    def _on_frame_configure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Update the width of the canvas window when the canvas is resized
        canvas_width = event.width
        self.canvas.itemconfig(
            self.canvas_window,
            width=canvas_width
        )

    def create_button_group(self, buttons):
        # Create a button group at the bottom of the modal
        button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20, padx=10)
        button_frame.grid_columnconfigure(1, weight=1)  # Center the buttons

        for idx, (text, command, colors) in enumerate(buttons):
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=140,  # Standardized button width
                height=40,  # Standardized button height
                fg_color=colors[0] if colors else THEME["colors"]["primary"],
                hover_color=colors[1] if colors else THEME["colors"]["primary_hover"],
                text_color="white",
                corner_radius=8
            )
            btn.pack(side="left", padx=5)

class LoadingIndicator:
    def __init__(self, parent, text="Loading..."):
        """Create a loading overlay with spinner"""
        self.overlay = ctk.CTkFrame(
            parent,
            fg_color=THEME["colors"]["surface"] + "CC",  # Add transparency
            corner_radius=0
        )
        
        self.container = ctk.CTkFrame(
            self.overlay,
            fg_color=THEME["colors"]["primary_light"],
            corner_radius=8
        )
        
        self.label = ctk.CTkLabel(
            self.container,
            text=text,
            font=THEME["fonts"]["body"],
            text_color=THEME["colors"]["text"]
        )
        
        self.spinner = self._create_spinner()
        
    def _create_spinner(self):
        """Create an animated loading spinner"""
        canvas = ctk.CTkCanvas(
            self.container,
            width=30,
            height=30,
            bg=THEME["colors"]["primary_light"],
            highlightthickness=0
        )
        
        # Create spinning arc
        self.angle = 0
        self.arc = canvas.create_arc(
            5, 5, 25, 25,
            start=self.angle,
            extent=300,
            outline=THEME["colors"]["primary"],
            width=2
        )
        
        return canvas
        
    def show(self):
        """Display the loading indicator"""
        # Position overlay to cover parent
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Center container
        self.container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add components
        self.spinner.pack(pady=10)
        self.label.pack(pady=(0, 10))
        
        # Start animation
        self._animate()
        
    def hide(self):
        """Hide the loading indicator"""
        self.overlay.place_forget()
        
    def _animate(self):
        """Animate the spinner"""
        self.angle = (self.angle + 10) % 360
        self.spinner.itemconfig(
            self.arc,
            start=self.angle
        )
        
        # Schedule next frame
        self.container.after(50, self._animate)
        
    def update_text(self, text):
        """Update the loading text"""
        self.label.configure(text=text)