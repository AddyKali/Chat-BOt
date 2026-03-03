"""
Enhanced Voice Assistant with Full Integration
Combines all modules for comprehensive system control
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

import speech_recognition as sr
import pyttsx3
import threading
import queue
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import anthropic

from file_manager import FileManager, AutomationEngine
from system_controller import SystemController, PowerManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedVoiceAssistant:
    """Enhanced voice assistant with full system integration"""
    
    def __init__(self, config_path: str = "configs/config.json"):
        self.config = self._load_config(config_path)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.wake_word = self.config.get("wake_word", "jarvis").lower()
        
        # Initialize modules
        self.file_manager = FileManager()
        self.system_controller = SystemController()
        self.automation_engine = AutomationEngine()
        self.power_manager = PowerManager()
        
        # Configure TTS
        self._configure_tts()
        
        # Initialize Claude API
        self.claude_client = None
        if self.config.get("anthropic_api_key"):
            self.claude_client = anthropic.Anthropic(
                api_key=self.config["anthropic_api_key"]
            )
        
        # Calibrate microphone
        with self.microphone as source:
            logger.info("Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        logger.info("Enhanced Voice Assistant initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "wake_word": "jarvis",
                "voice_rate": 180,
                "voice_volume": 0.9,
                "anthropic_api_key": None
            }
    
    def _configure_tts(self):
        """Configure text-to-speech"""
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        self.tts_engine.setProperty('rate', self.config.get('voice_rate', 180))
        self.tts_engine.setProperty('volume', self.config.get('voice_volume', 0.9))
    
    def speak(self, text: str):
        """Text to speech"""
        logger.info(f"Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self) -> Optional[str]:
        """Listen and convert speech to text"""
        try:
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            logger.info("Processing...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text.lower()
        
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return None
    
    def process_with_claude(self, command: str) -> str:
        """Process command with Claude API"""
        if not self.claude_client:
            return "Claude API not configured."
        
        try:
            message = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system="You are an intelligent voice assistant. Provide concise, conversational responses.",
                messages=[{"role": "user", "content": command}]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return "Sorry, AI processing unavailable."
    
    def process_command(self, command: str):
        """Main command processor"""
        if not command:
            return
        
        cmd = command.lower()
        
        # Exit commands
        if any(word in cmd for word in ["exit", "quit", "goodbye", "stop"]):
            self.speak("Goodbye!")
            self.is_listening = False
            return
        
        # Time/Date
        if "time" in cmd:
            self.speak(f"The time is {datetime.now().strftime('%I:%M %p')}")
            return
        if "date" in cmd:
            self.speak(f"Today is {datetime.now().strftime('%B %d, %Y')}")
            return
        
        # File Management Commands
        if "create folder" in cmd or "make folder" in cmd:
            folder_name = cmd.replace("create folder", "").replace("make folder", "").strip()
            if self.file_manager.create_folder(folder_name):
                self.speak(f"Created folder {folder_name}")
            return
        
        if "list files" in cmd:
            location = "desktop"
            if "downloads" in cmd:
                location = "downloads"
            elif "documents" in cmd:
                location = "documents"
            
            files = self.file_manager.list_files(location)
            if files:
                self.speak(f"Found {len(files)} files in {location}")
            else:
                self.speak(f"No files found in {location}")
            return
        
        if "organize downloads" in cmd:
            if self.automation_engine.organize_downloads():
                self.speak("Downloads folder organized")
            return
        
        if "clean temp" in cmd or "clean temporary" in cmd:
            if self.automation_engine.clean_temp_files():
                self.speak("Temporary files cleaned")
            return
        
        # System Control Commands
        if "running processes" in cmd or "list processes" in cmd:
            processes = self.system_controller.get_running_processes()
            self.speak(f"There are {len(processes)} processes running")
            return
        
        if "disk space" in cmd or "disk usage" in cmd:
            disks = self.system_controller.get_disk_usage()
            for drive, info in disks.items():
                self.speak(f"Drive {drive}: {info['free_gb']} GB free out of {info['total_gb']} GB")
            return
        
        if "minimize windows" in cmd or "show desktop" in cmd:
            if self.system_controller.minimize_all_windows():
                self.speak("All windows minimized")
            return
        
        if "screenshot" in cmd or "take screenshot" in cmd:
            if self.system_controller.take_screenshot():
                self.speak("Screenshot taken")
            return
        
        if "empty recycle bin" in cmd:
            if self.system_controller.empty_recycle_bin():
                self.speak("Recycle bin emptied")
            return
        
        if "dark mode" in cmd:
            enable = "enable" in cmd or "on" in cmd
            if self.system_controller.enable_dark_mode(enable):
                self.speak(f"Dark mode {'enabled' if enable else 'disabled'}")
            return
        
        if "wifi networks" in cmd or "available networks" in cmd:
            networks = self.system_controller.get_wifi_networks()
            if networks:
                self.speak(f"Found {len(networks)} WiFi networks")
            return
        
        # Power Management
        if "hibernate" in cmd:
            self.speak("Hibernating now")
            self.power_manager.hibernate()
            return
        
        if "prevent sleep" in cmd:
            enable = "enable" in cmd or "on" in cmd
            if self.power_manager.prevent_sleep(enable):
                self.speak(f"Sleep prevention {'enabled' if enable else 'disabled'}")
            return
        
        # Basic system commands (from original)
        if "battery" in cmd:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                self.speak(f"Battery at {battery.percent} percent")
            return
        
        if "cpu" in cmd:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            self.speak(f"CPU usage is {cpu} percent")
            return
        
        if "memory" in cmd or "ram" in cmd:
            import psutil
            memory = psutil.virtual_memory()
            self.speak(f"Memory usage is {memory.percent} percent")
            return
        
        # Application launching
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "word": "winword.exe",
            "excel": "excel.exe"
        }
        
        for app_name, app_exe in apps.items():
            if app_name in cmd and "open" in cmd:
                import subprocess
                subprocess.Popen(app_exe, shell=True)
                self.speak(f"Opening {app_name}")
                return
        
        # Web search
        if "search" in cmd or "google" in cmd:
            query = cmd.replace("search", "").replace("google", "").strip()
            if query:
                import webbrowser
                webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
                self.speak(f"Searching for {query}")
            return
        
        # Use Claude for everything else
        if self.claude_client:
            response = self.process_with_claude(command)
            self.speak(response)
        else:
            self.speak("I don't understand that command")
    
    def start(self):
        """Start the voice assistant"""
        self.is_listening = True
        self.speak(f"Enhanced voice assistant activated. Say {self.wake_word} to give commands.")
        
        while self.is_listening:
            try:
                command = self.listen()
                
                if command:
                    if self.wake_word in command:
                        self.speak("Yes?")
                        actual_command = self.listen()
                        if actual_command:
                            self.process_command(actual_command)
                    else:
                        self.process_command(command)
            
            except KeyboardInterrupt:
                self.speak("Shutting down")
                self.is_listening = False
                break
            except Exception as e:
                logger.error(f"Error: {e}")


def main():
    """Entry point"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("configs", exist_ok=True)
    
    config_path = "configs/config.json"
    if not os.path.exists(config_path):
        default_config = {
            "wake_word": "jarvis",
            "voice_rate": 180,
            "voice_volume": 0.9,
            "anthropic_api_key": None
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    assistant = EnhancedVoiceAssistant(config_path)
    assistant.start()


if __name__ == "__main__":
    main()
