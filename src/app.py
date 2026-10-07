import queue
import threading
import customtkinter as ctk
import os
import sys
import mouse_actions as m
from parser import parse_all, Command
from voice_vosk import VoskListener
from controller import CommandRunner
import ctypes
from PIL import Image

COUNTDOWN_SECONDS = 3

def resource_path(relative):
    """Find files both in normal runs and inside a packaged exe."""
    if hasattr(sys, "_MEIPASS"):                       # running as exe
        base = sys._MEIPASS
    else:                                              # running from source
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.title("Voice clicker")
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("voiceclicker.app")
        except Exception:
            pass
        self.after(250, lambda: self.iconbitmap(resource_path("assets/logo.ico")))
        self.geometry("460x660")
        self.resizable(False, False)

        # Threads never touch widgets. They put events here instead.
        self.events = queue.Queue()
        self.runner = CommandRunner(on_log=lambda msg: self.events.put(("log", msg)))
        self.listener = VoskListener(
            on_text=lambda t: self.events.put(("heard", t)),
            on_status=lambda s: self.events.put(("status", s)),
            model_path=resource_path("model"),
        )
        self.voice_on = False
        self._countdown_job = None

        self.action_var = ctk.StringVar(value="click")
        self.button_var = ctk.StringVar(value="left")

        self.build_ui()
        self.on_action_change()
        self.poll_events()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- layout ----------
    def build_ui(self):
        pad = {"padx": 16, "pady": 8}

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", **pad)
        logo_img = ctk.CTkImage(
            light_image=Image.open(resource_path("assets/logo.png")),
            dark_image=Image.open(resource_path("assets/logo.png")),
            size=(32, 32),
        )
        ctk.CTkLabel(header, image=logo_img, text="  Voice clicker",
                     compound="left",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        self.status_label = ctk.CTkLabel(header, text="Ready", text_color="gray")
        self.status_label.pack(side="right")

        voice_card = ctk.CTkFrame(self)
        voice_card.pack(fill="x", **pad)
        text_col = ctk.CTkFrame(voice_card, fg_color="transparent")
        text_col.pack(side="left", padx=12, pady=12)
        ctk.CTkLabel(text_col, text="Voice mode",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(text_col, text="Say a command, or say stop",
                     text_color="gray").pack(anchor="w")
        self.voice_btn = ctk.CTkButton(voice_card, text="Enable voice",
                                       width=120, command=self.toggle_voice)
        self.voice_btn.pack(side="right", padx=12)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", **pad)
        ctk.CTkLabel(action_frame, text="Action", text_color="gray").pack(anchor="w")
        row = ctk.CTkFrame(action_frame, fg_color="transparent")
        row.pack(anchor="w", pady=4)
        for label, value in [("Click", "click"), ("Double", "double"),
                             ("Hold", "hold"), ("Repeat", "repeat")]:
            ctk.CTkRadioButton(row, text=label, value=value,
                               variable=self.action_var,
                               command=self.on_action_change).pack(side="left", padx=(0, 14))

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", **pad)
        ctk.CTkLabel(button_frame, text="Mouse button", text_color="gray").pack(anchor="w")
        row = ctk.CTkFrame(button_frame, fg_color="transparent")
        row.pack(anchor="w", pady=4)
        for label, value in [("Left", "left"), ("Right", "right")]:
            ctk.CTkRadioButton(row, text=label, value=value,
                               variable=self.button_var).pack(side="left", padx=(0, 14))

        options = ctk.CTkFrame(self, fg_color="transparent")
        options.pack(fill="x", **pad)
        options.columnconfigure((0, 1), weight=1)

        self.duration_frame = ctk.CTkFrame(options, fg_color="transparent")
        self.duration_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.duration_label = ctk.CTkLabel(self.duration_frame, text="Duration (seconds)",
                                           text_color="gray")
        self.duration_label.pack(anchor="w")
        self.duration_entry = ctk.CTkEntry(self.duration_frame)
        self.duration_entry.pack(fill="x")
        self.duration_entry.insert(0, "5")

        self.interval_frame = ctk.CTkFrame(options, fg_color="transparent")
        self.interval_frame.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(self.interval_frame, text="Interval (seconds)",
                     text_color="gray").pack(anchor="w")
        self.interval_entry = ctk.CTkEntry(self.interval_frame)
        self.interval_entry.pack(fill="x")
        self.interval_entry.insert(0, "1")

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", **pad)
        buttons.columnconfigure((0, 1), weight=1)
        ctk.CTkButton(buttons, text="Run now", command=self.run_now).grid(
            row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(buttons, text="Stop", fg_color="#c0392b", hover_color="#962d22",
                      command=self.stop_all).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        log_frame = ctk.CTkFrame(self, fg_color="transparent")
        log_frame.pack(fill="both", expand=True, **pad)
        ctk.CTkLabel(log_frame, text="Command log", text_color="gray").pack(anchor="w")
        self.log_box = ctk.CTkTextbox(log_frame, state="disabled",
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(fill="both", expand=True, pady=4)

    # ---------- helpers ----------
    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    @staticmethod
    def set_entry(entry, value):
        entry.delete(0, "end")
        entry.insert(0, f"{value:g}")

    def on_action_change(self):
        action = self.action_var.get()
        label = "Total time (seconds)" if action == "repeat" else "Duration (seconds)"
        self.duration_label.configure(text=label)
        if action == "repeat":
            self.interval_frame.grid()
        else:
            self.interval_frame.grid_remove()

    def read_form(self):
        try:
            seconds = float(self.duration_entry.get())
            interval = float(self.interval_entry.get())
        except ValueError:
            self.log("Enter numbers for duration and interval")
            return None
        if seconds <= 0 or interval <= 0:
            self.log("Duration and interval must be above zero")
            return None
        return Command(self.action_var.get(), self.button_var.get(), seconds, interval)

    # ---------- buttons ----------
    def run_now(self):
        cmd = self.read_form()
        if cmd:
            self.countdown(COUNTDOWN_SECONDS, cmd)

    def countdown(self, n, cmd):
        if n > 0:
            self.status_label.configure(text=f"Starting in {n}... move your cursor")
            self._countdown_job = self.after(1000, self.countdown, n - 1, cmd)
        else:
            self._countdown_job = None
            self.status_label.configure(text="Running")
            self.runner.submit(cmd)

    def stop_all(self):
        if self._countdown_job:
            self.after_cancel(self._countdown_job)
            self._countdown_job = None
        self.runner.submit(Command("stop"))
        self.status_label.configure(text="Stopped")

    def toggle_voice(self):
        if self.voice_on:
            self.voice_on = False
            self.voice_btn.configure(text="Enable voice")
            self.listener.stop()
        else:
            self.voice_on = True
            self.voice_btn.configure(text="Disable voice")
            threading.Thread(target=self._start_voice, daemon=True).start()

    def _start_voice(self):
        try:
            self.listener.start()
        except Exception as e:
            self.events.put(("log", f"Microphone error: {e}"))
            self.events.put(("voice_failed", None))

    # ---------- events from background threads ----------
    def poll_events(self):
        while True:
            try:
                kind, data = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self.log(data)
            elif kind == "status":
                self.status_label.configure(text=data)
            elif kind == "heard":
                self.handle_speech(data)
            elif kind == "voice_failed":
                self.voice_on = False
                self.voice_btn.configure(text="Enable voice")
        self.after(50, self.poll_events)

    def handle_speech(self, text):
        self.log(f'Heard: "{text}"')
        commands = parse_all(text)
        if not commands:
            self.log("Not understood")
            return
        for cmd in commands:
            self.apply_command(cmd)

    def apply_command(self, cmd):
        if cmd.action == "set":
            entry = self.interval_entry if cmd.field == "interval" else self.duration_entry
            self.set_entry(entry, cmd.seconds)
            self.log(f"{cmd.field.capitalize()} set to {cmd.seconds:g} seconds")
            return

        if cmd.action == "run":
            form = self.read_form()
            if form:
                self.runner.submit(form)
            return

        if cmd.action != "stop":
            self.action_var.set(cmd.action)
            self.button_var.set(cmd.button)
            if cmd.action in ("hold", "repeat"):
                self.set_entry(self.duration_entry, cmd.seconds)
            if cmd.action == "repeat":
                self.set_entry(self.interval_entry, cmd.interval)
            self.on_action_change()
        self.runner.submit(cmd)

    def on_close(self):
        self.listener.stop()
        m.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()