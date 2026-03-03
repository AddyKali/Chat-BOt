import customtkinter as ctk
import threading
import subprocess
import time
import math

# -----------------------------
# JARVIS OS LEVEL UI
# Floating Orb + Ring + Always On Top
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VoiceAssistantUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup (floating assistant style)
        self.title("JARVIS")
        self.geometry("320x380")
        self.resizable(False, False)
        self.overrideredirect(False)
        self.attributes("-topmost", True)

        self.process = None
        self.animation_running = False
        self.current_state = "Idle"
        self.angle = 0

        # -----------------------------
        # HEADER
        # -----------------------------
        self.title_label = ctk.CTkLabel(
            self,
            text="JARVIS",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(pady=(10, 0))

        self.state_var = ctk.StringVar(value="Idle")
        self.state_label = ctk.CTkLabel(
            self,
            textvariable=self.state_var,
            font=ctk.CTkFont(size=14)
        )
        self.state_label.pack(pady=(0, 5))

        # -----------------------------
        # ORB CANVAS
        # -----------------------------
        self.canvas = ctk.CTkCanvas(
            self, width=240, height=240,
            bg="#020617", highlightthickness=0
        )
        self.canvas.pack(pady=5)

        self.center_x = 120
        self.center_y = 120

        self.outer_ring = self.canvas.create_oval(
            20, 20, 220, 220,
            outline="#3b8ed0", width=3
        )

        self.inner_ring = self.canvas.create_oval(
            50, 50, 190, 190,
            outline="#1f6aa5", width=2
        )

        self.core = self.canvas.create_oval(
            95, 95, 145, 145,
            fill="#0ea5e9", outline=""
        )

        # -----------------------------
        # MINI CONTROLS
        # -----------------------------
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(pady=5)

        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start",
            command=self.start_assistant,
            width=90,
            height=28
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ctk.CTkButton(
            control_frame,
            text="Stop",
            command=self.stop_assistant,
            width=90,
            height=28,
            fg_color="red"
        )
        self.stop_button.grid(row=0, column=1, padx=5)

        self.log_box = ctk.CTkTextbox(self, width=280, height=70)
        self.log_box.pack(pady=(5, 10))

        self.log("JARVIS OS Ready...")

    # -----------------------------
    # STATE CONTROL
    # -----------------------------
    def set_state(self, state):
        self.current_state = state
        self.state_var.set(state)

        if state in ["Listening", "Thinking", "Speaking"]:
            self.start_animation()
        else:
            self.stop_animation()

    # -----------------------------
    # LOGGING
    # -----------------------------
    def log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

        msg_lower = message.lower()

        if "listening" in msg_lower:
            self.set_state("Listening")
        elif "thinking" in msg_lower or "processing" in msg_lower:
            self.set_state("Thinking")
        elif "speaking" in msg_lower:
            self.set_state("Speaking")

    # -----------------------------
    # ORB ANIMATION
    # -----------------------------
    def animate_orb(self):
        self.animation_running = True

        while self.animation_running:
            pulse = abs(math.sin(self.angle)) * 10
            glow = int(120 + abs(math.sin(self.angle)) * 80)

            color = f"#{glow:02x}8ed0"

            # outer pulse
            self.canvas.coords(
                self.outer_ring,
                20 - pulse,
                20 - pulse,
                220 + pulse,
                220 + pulse
            )
            self.canvas.itemconfig(self.outer_ring, outline=color)

            # core color by state
            if self.current_state == "Listening":
                self.canvas.itemconfig(self.core, fill="#0ea5e9")
            elif self.current_state == "Thinking":
                self.canvas.itemconfig(self.core, fill="#eab308")
            elif self.current_state == "Speaking":
                self.canvas.itemconfig(self.core, fill="#22c55e")
            else:
                self.canvas.itemconfig(self.core, fill="#1f2937")

            self.angle += 0.07
            time.sleep(0.03)

    def start_animation(self):
        if not self.animation_running:
            threading.Thread(target=self.animate_orb, daemon=True).start()

    def stop_animation(self):
        self.animation_running = False

    # -----------------------------
    # ASSISTANT CONTROL
    # -----------------------------
    def start_assistant(self):
        if self.process is None:
            self.log("Starting assistant...")

            def run():
                self.process = subprocess.Popen(
                    ["venv\\Scripts\\python.exe", "enhanced_main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                for line in self.process.stdout:
                    self.log(line.strip())

            threading.Thread(target=run, daemon=True).start()

    def stop_assistant(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self.set_state("Idle")
            self.log("Assistant stopped.")


if __name__ == "__main__":
    app = VoiceAssistantUI()
    app.mainloop()