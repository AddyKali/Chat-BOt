"""
GUI Launcher for Voice Assistant
Provides an easy-to-use interface for starting and configuring the assistant
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import subprocess
import threading
import os
from pathlib import Path

class VoiceAssistantLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant Launcher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Load config
        self.config_path = "configs/config.json"
        self.config = self.load_config()
        
        # Process reference
        self.assistant_process = None
        
        self.create_widgets()
    
    def load_config(self):
        """Load configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except:
            return {
                "wake_word": "jarvis",
                "voice_rate": 180,
                "voice_volume": 0.9,
                "anthropic_api_key": None
            }
    
    def save_config(self):
        """Save configuration file"""
        try:
            os.makedirs("configs", exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="Voice Assistant Control Panel",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuration Section
        config_label = tk.Label(
            main_frame,
            text="Configuration",
            font=("Arial", 12, "bold")
        )
        config_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Wake Word
        tk.Label(main_frame, text="Wake Word:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.wake_word_entry = tk.Entry(main_frame, width=30)
        self.wake_word_entry.insert(0, self.config.get("wake_word", "jarvis"))
        self.wake_word_entry.grid(row=1, column=1, pady=5)
        
        # Voice Rate
        tk.Label(main_frame, text="Voice Speed:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.voice_rate_scale = tk.Scale(
            main_frame,
            from_=100,
            to=250,
            orient=tk.HORIZONTAL,
            length=200
        )
        self.voice_rate_scale.set(self.config.get("voice_rate", 180))
        self.voice_rate_scale.grid(row=2, column=1, pady=5)
        
        # Voice Volume
        tk.Label(main_frame, text="Voice Volume:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.voice_volume_scale = tk.Scale(
            main_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            length=200
        )
        self.voice_volume_scale.set(self.config.get("voice_volume", 0.9))
        self.voice_volume_scale.grid(row=3, column=1, pady=5)
        
        # API Key
        tk.Label(main_frame, text="Anthropic API Key:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = tk.Entry(main_frame, width=30, show="*")
        if self.config.get("anthropic_api_key"):
            self.api_key_entry.insert(0, self.config.get("anthropic_api_key"))
        self.api_key_entry.grid(row=4, column=1, pady=5)
        
        # Save Config Button
        save_btn = tk.Button(
            main_frame,
            text="Save Configuration",
            command=self.save_configuration,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        save_btn.grid(row=5, column=0, columnspan=2, pady=15)
        
        # Control Section
        control_label = tk.Label(
            main_frame,
            text="Control",
            font=("Arial", 12, "bold")
        )
        control_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 10))
        
        # Control Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start Assistant",
            command=self.start_assistant,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="■ Stop Assistant",
            command=self.stop_assistant,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(
            main_frame,
            text="Status: Not Running",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        self.status_label.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Quick Commands
        commands_label = tk.Label(
            main_frame,
            text="Quick Commands Reference",
            font=("Arial", 10, "bold")
        )
        commands_label.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        commands_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            width=60,
            font=("Courier", 9)
        )
        commands_text.grid(row=10, column=0, columnspan=2, pady=5)
        
        commands = """
• "What time is it?" - Get current time
• "Open notepad" - Launch applications
• "Take screenshot" - Capture screen
• "Battery status" - Check battery
• "Search for [query]" - Web search
• "Create folder [name]" - Make new folder
• "Organize downloads" - Auto-organize files
• "Enable dark mode" - Toggle dark mode
        """
        commands_text.insert(tk.END, commands)
        commands_text.config(state=tk.DISABLED)
    
    def save_configuration(self):
        """Save current configuration"""
        self.config["wake_word"] = self.wake_word_entry.get()
        self.config["voice_rate"] = int(self.voice_rate_scale.get())
        self.config["voice_volume"] = float(self.voice_volume_scale.get())
        
        api_key = self.api_key_entry.get()
        self.config["anthropic_api_key"] = api_key if api_key else None
        
        self.save_config()
    
    def start_assistant(self):
        """Start the voice assistant"""
        # Save config first
        self.save_configuration()
        
        # Start assistant in separate thread
        def run():
            try:
                self.assistant_process = subprocess.Popen(
                    ["python", "enhanced_main.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.status_label.config(text="Status: Running", fg="#27ae60")
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start assistant: {e}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def stop_assistant(self):
        """Stop the voice assistant"""
        if self.assistant_process:
            self.assistant_process.terminate()
            self.assistant_process = None
            self.status_label.config(text="Status: Not Running", fg="#7f8c8d")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def on_closing(self):
        """Handle window close"""
        if self.assistant_process:
            self.stop_assistant()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = VoiceAssistantLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
