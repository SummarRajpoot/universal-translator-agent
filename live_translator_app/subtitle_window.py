import tkinter as tk

class SubtitleWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live Subtitles")
        
        # Window properties
        self.root.overrideredirect(True) # Remove title bar
        self.root.attributes("-topmost", True) # Always on top
        self.root.attributes("-transparentcolor", "black") # Transparent background (Windows only)
        self.root.configure(bg="black")
        
        # Screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Initial Position (Bottom)
        self.root.geometry(f"{screen_width}x100+0+{screen_height - 150}")
        
        # Label for subtitles
        self.label = tk.Label(
            self.root,
            text="Waiting for audio...",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="black",
            wraplength=screen_width - 100,
            justify="center"
        )
        self.label.pack(expand=True, fill="both")

        # Draggable functionality
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        x = max(0, min(x, self.root.winfo_screenwidth() - self.root.winfo_width()))
        y = self.root.winfo_y() + deltay
        y = max(0, min(y, self.root.winfo_screenheight() - self.root.winfo_height()))
        self.root.geometry(f"+{x}+{y}")

    def update_text(self, text):
        self.label.config(text=text)
        # Auto-fade logic or timer could go here
        
    def set_font_size(self, size):
        self.label.config(font=("Arial", size, "bold"))

    def show(self):
        self.root.update()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    sub = SubtitleWindow()
    sub.update_text("This is a live translation test.")
    sub.run()
