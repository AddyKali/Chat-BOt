"""
Advanced Voice-Controlled AI Assistant for Windows
Supports speech recognition, Claude API integration, and full system control
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import json
import os
import subprocess
import psutil
import webbrowser
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Dict, Any
import anthropic

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


class VoiceAssistant:
    """Main voice assistant class with AI and system control capabilities"""
    
    def __init__(self, config_path: str = "configs/config.json"):
        self.config = self._load_config(config_path)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.command_queue = queue.Queue()
        self.is_listening = False
        self.wake_word = self.config.get("wake_word", "jarvis").lower()
        
        # Configure TTS
        self._configure_tts()
        
        # Initialize Claude API if key provided
        self.claude_client = None
        if self.config.get("anthropic_api_key"):
            self.claude_client = anthropic.Anthropic(
                api_key=self.config["anthropic_api_key"]
            )
        
        # Adjust for ambient noise
        with self.microphone as source:
            logger.info("Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        logger.info("Voice Assistant initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return {
                "wake_word": "jarvis",
                "voice_rate": 180,
                "voice_volume": 0.9,
                "anthropic_api_key": None
            }
    
    def _configure_tts(self):
        """Configure text-to-speech engine"""
        voices = self.tts_engine.getProperty('voices')
        # Try to use a natural voice (usually index 1 on Windows)
        if len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        
        self.tts_engine.setProperty('rate', self.config.get('voice_rate', 180))
        self.tts_engine.setProperty('volume', self.config.get('voice_volume', 0.9))
    
    def speak(self, text: str):
        """Convert text to speech"""
        logger.info(f"Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            logger.info("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text.lower()
        
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            self.speak("Sorry, there was an error with speech recognition")
            return None
    
    def process_with_claude(self, command: str) -> str:
        """Process command using Claude API for intelligent responses"""
        if not self.claude_client:
            return "Claude API not configured. Please add your API key to the config."
        
        try:
            system_prompt = """You are an intelligent voice assistant running on a Windows laptop. 
            You help users with tasks, answer questions, and provide information.
            Keep responses concise and conversational for voice output.
            If asked to perform system tasks, describe what you would do clearly."""
            
            message = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": command}]
            )
            
            response = message.content[0].text
            logger.info(f"Claude response: {response}")
            return response
        
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return "Sorry, I couldn't process that with AI right now."
    
    def execute_system_command(self, command: str) -> bool:
        """Execute system-level commands"""
        command_lower = command.lower()
        
        try:
            # Open applications
            if "open" in command_lower:
                return self._open_application(command_lower)
            
            # File operations
            elif "create file" in command_lower or "new file" in command_lower:
                return self._create_file(command_lower)
            
            # Web browsing
            elif "search" in command_lower or "google" in command_lower:
                return self._web_search(command_lower)
            
            # System information
            elif "battery" in command_lower:
                return self._get_battery_info()
            
            elif "cpu" in command_lower or "processor" in command_lower:
                return self._get_cpu_info()
            
            elif "memory" in command_lower or "ram" in command_lower:
                return self._get_memory_info()
            
            # Volume control
            elif "volume" in command_lower:
                return self._control_volume(command_lower)
            
            # Shutdown/Restart
            elif "shutdown" in command_lower:
                return self._shutdown_system()
            
            elif "restart" in command_lower:
                return self._restart_system()
            
            # Lock screen
            elif "lock" in command_lower:
                return self._lock_screen()
            
            return False
        
        except Exception as e:
            logger.error(f"Error executing system command: {e}")
            self.speak(f"Sorry, there was an error executing that command")
            return False
    
    def _open_application(self, command: str) -> bool:
        """Open Windows applications"""
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "explorer": "explorer.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "cmd": "cmd.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:"
        }
        
        for app_name, app_exe in apps.items():
            if app_name in command:
                try:
                    if app_exe == "ms-settings:":
                        os.startfile(app_exe)
                    else:
                        subprocess.Popen(app_exe, shell=True)
                    self.speak(f"Opening {app_name}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to open {app_name}: {e}")
                    self.speak(f"Sorry, I couldn't open {app_name}")
                    return False
        
        return False
    
    def _create_file(self, command: str) -> bool:
        """Create a new file"""
        try:
            desktop = Path.home() / "Desktop"
            filename = f"new_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = desktop / filename
            
            filepath.touch()
            self.speak(f"Created {filename} on your desktop")
            return True
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            return False
    
    def _web_search(self, command: str) -> bool:
        """Perform web search"""
        try:
            # Extract search query
            query = command.replace("search", "").replace("google", "").strip()
            if query:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(url)
                self.speak(f"Searching for {query}")
                return True
        except Exception as e:
            logger.error(f"Web search error: {e}")
        return False
    
    def _get_battery_info(self) -> bool:
        """Get battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "plugged in" if battery.power_plugged else "not plugged in"
                self.speak(f"Battery is at {percent} percent and {plugged}")
                return True
            else:
                self.speak("No battery detected")
                return True
        except Exception as e:
            logger.error(f"Battery info error: {e}")
            return False
    
    def _get_cpu_info(self) -> bool:
        """Get CPU usage information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.speak(f"CPU usage is at {cpu_percent} percent")
            return True
        except Exception as e:
            logger.error(f"CPU info error: {e}")
            return False
    
    def _get_memory_info(self) -> bool:
        """Get memory usage information"""
        try:
            memory = psutil.virtual_memory()
            self.speak(f"Memory usage is at {memory.percent} percent")
            return True
        except Exception as e:
            logger.error(f"Memory info error: {e}")
            return False
    
    def _control_volume(self, command: str) -> bool:
        """Control system volume using nircmd"""
        try:
            if "mute" in command:
                subprocess.run(["nircmd.exe", "mutesysvolume", "1"], shell=True)
                self.speak("Volume muted")
            elif "unmute" in command:
                subprocess.run(["nircmd.exe", "mutesysvolume", "0"], shell=True)
                self.speak("Volume unmuted")
            elif "up" in command or "increase" in command:
                subprocess.run(["nircmd.exe", "changesysvolume", "2000"], shell=True)
                self.speak("Volume increased")
            elif "down" in command or "decrease" in command:
                subprocess.run(["nircmd.exe", "changesysvolume", "-2000"], shell=True)
                self.speak("Volume decreased")
            return True
        except Exception as e:
            logger.error(f"Volume control error: {e}")
            self.speak("Volume control requires nircmd utility")
            return False
    
    def _shutdown_system(self) -> bool:
        """Shutdown the system"""
        self.speak("Shutting down in 10 seconds. Say cancel to abort.")
        # Give user time to cancel
        return True
    
    def _restart_system(self) -> bool:
        """Restart the system"""
        self.speak("Restarting in 10 seconds. Say cancel to abort.")
        return True
    
    def _lock_screen(self) -> bool:
        """Lock the Windows screen"""
        try:
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)
            return True
        except Exception as e:
            logger.error(f"Lock screen error: {e}")
            return False
    
    def process_command(self, command: str):
        """Main command processing logic"""
        if not command:
            return
        
        # Remove wake word if present
        command = command.replace(self.wake_word, "").strip()
        
        # Exit command
        if any(word in command for word in ["exit", "quit", "goodbye", "stop listening"]):
            self.speak("Goodbye!")
            self.is_listening = False
            return
        
        # Time query
        if "time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {current_time}")
            return
        
        # Date query
        if "date" in command:
            current_date = datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
            return
        
        # Try system commands first
        if self.execute_system_command(command):
            return
        
        # Use Claude API for general queries
        if self.claude_client:
            response = self.process_with_claude(command)
            self.speak(response)
        else:
            self.speak("I don't understand that command. Claude API is not configured for advanced queries.")
    
    def start(self):
        """Start the voice assistant"""
        self.is_listening = True
        self.speak(f"Voice assistant activated. Say {self.wake_word} to give commands.")
        
        while self.is_listening:
            try:
                command = self.listen()
                
                if command:
                    # Check for wake word
                    if self.wake_word in command:
                        self.speak("Yes?")
                        # Listen for actual command
                        actual_command = self.listen()
                        if actual_command:
                            self.process_command(actual_command)
                    else:
                        # Process direct commands too
                        self.process_command(command)
            
            except KeyboardInterrupt:
                logger.info("Stopping assistant...")
                self.speak("Shutting down voice assistant")
                self.is_listening = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                continue


def main():
    """Main entry point"""
    # Ensure directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("configs", exist_ok=True)
    
    # Create default config if it doesn't exist
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
        print(f"Created default config at {config_path}")
        print("Add your Anthropic API key to enable Claude integration!")
    
    # Start assistant
    assistant = VoiceAssistant(config_path)
    assistant.start()


if __name__ == "__main__":
    main()
