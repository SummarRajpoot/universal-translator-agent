import threading
import time
import tkinter as tk
from tkinter import ttk
from audio_capture import AudioCapture
from transcriber import Transcriber
from translator import Translator
from subtitle_window import SubtitleWindow

class LiveTranslatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live Translator Settings")
        self.root.geometry("400x500")

        # Components
        self.audio = AudioCapture()
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.subtitle_win = SubtitleWindow()

        self.running = False
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.root, text="Live Translator Settings", font=("Arial", 16, "bold")).pack(pady=10)

        # Language selection
        ttk.Label(self.root, text="Target Language:").pack()
        self.lang_var = tk.StringVar(value="Urdu")
        self.lang_dropdown = ttk.Combobox(self.root, textvariable=self.lang_var)
        self.lang_dropdown['values'] = ("English", "Urdu", "Arabic", "French", "Spanish", "German", "Hindi", "Japanese", "Chinese")
        self.lang_dropdown.pack(pady=5)

        # Font size
        ttk.Label(self.root, text="Font Size:").pack()
        self.font_size = tk.Scale(self.root, from_=10, to_=50, orient="horizontal", command=self.update_font)
        self.font_size.set(24)
        self.font_size.pack(pady=5)

        # Buttons
        self.start_btn = ttk.Button(self.root, text="START TRANSLATION", command=self.toggle)
        self.start_btn.pack(pady=20)

        ttk.Label(self.root, text="Hint: Drag the subtitle window anywhere.", font=("Arial", 8)).pack(side="bottom")

    def update_font(self, val):
        self.subtitle_win.set_font_size(int(val))

    def toggle(self):
        if not self.running:
            self.running = True
            self.start_btn.config(text="STOP TRANSLATION")
            threading.Thread(target=self.run_loop, daemon=True).start()
        else:
            self.running = False
            self.start_btn.config(text="START TRANSLATION")
            self.audio.stop_capture()

    def run_loop(self):
        self.audio.start_capture()
        while self.running:
            audio_data = self.audio.get_audio_chunk()
            if audio_data is not None and len(audio_data) > 3200: # Min 0.2s
                # 1. Transcribe
                text, detected_lang = self.transcriber.transcribe(audio_data)
                if text:
                    print(f"Transcribed ({detected_lang}): {text}")
                    
                    # 2. Translate
                    target = self.lang_var.get()
                    translated = self.translator.translate(text, target_lang=target)
                    print(f"Translated ({target}): {translated}")
                    
                    # 3. Update Subtitles
                    self.subtitle_win.root.after(0, self.subtitle_win.update_text, translated)
            
            time.sleep(0.5)

    def run(self):
        # Run subtitle window update in background or separate loop
        self.root.mainloop()

if __name__ == "__main__":
    app = LiveTranslatorApp()
    app.run()
