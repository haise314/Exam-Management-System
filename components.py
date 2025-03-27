import customtkinter as ctk
from config import THEME

class BaseModal(ctk.CTkToplevel):
    def __init__(self, parent, title, size="400x500"):
        super().__init__(parent)
        
        # Update modal styling
        self.title(title)
        self.geometry(size)
        self.configure(fg_color=THEME["colors"]["surface"])
        
        # Update container styling
        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Update title styling
        self.title_label = ctk.CTkLabel(
            self.container,
            text=title,
            font=THEME["fonts"]["subheading"],
            text_color=THEME["colors"]["text"]
        )
        self.title_label.pack(pady=(0, 20))

    def create_button_group(self, buttons):
        button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        button_frame.pack(pady=20)
        
        for text, command, colors in buttons:
            ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=100,
                fg_color=colors[0] if colors else THEME["colors"]["primary"],
                hover_color=colors[1] if colors else THEME["colors"]["primary_hover"],
                text_color="white"
            ).pack(side="left", padx=5) 