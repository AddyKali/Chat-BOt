"""
Advanced System Control Module
Handles system settings, processes, and hardware control
"""

import psutil
import subprocess
import win32api
import win32con
import win32gui
import ctypes
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SystemController:
    """Advanced system control operations"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def get_running_processes(self) -> List[Dict[str, any]]:
        """Get list of running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes
        except Exception as e:
            logger.error(f"Failed to get processes: {e}")
            return []
    
    def kill_process(self, process_name: str) -> bool:
        """Kill a process by name"""
        try:
            killed = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    proc.kill()
                    killed = True
                    logger.info(f"Killed process: {process_name}")
            return killed
        except Exception as e:
            logger.error(f"Failed to kill process: {e}")
            return False
    
    def get_disk_usage(self) -> Dict[str, Dict[str, any]]:
        """Get disk usage for all drives"""
        try:
            disks = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks[partition.device] = {
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent
                    }
                except PermissionError:
                    continue
            return disks
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}")
            return {}
    
    def get_network_info(self) -> Dict[str, any]:
        """Get network statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {}
    
    def set_brightness(self, level: int) -> bool:
        """Set screen brightness (0-100)"""
        try:
            # This requires WMI on Windows
            import wmi
            c = wmi.WMI(namespace='wmi')
            methods = c.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(level, 0)
            logger.info(f"Set brightness to {level}%")
            return True
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return False
    
    def get_active_window(self) -> Optional[str]:
        """Get the title of the active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    def minimize_all_windows(self) -> bool:
        """Minimize all windows (Windows+D)"""
        try:
            self.user32.keybd_event(win32con.VK_LWIN, 0, 0, 0)
            self.user32.keybd_event(ord('D'), 0, 0, 0)
            self.user32.keybd_event(ord('D'), 0, win32con.KEYEVENTF_KEYUP, 0)
            self.user32.keybd_event(win32con.VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)
            logger.info("Minimized all windows")
            return True
        except Exception as e:
            logger.error(f"Failed to minimize windows: {e}")
            return False
    
    def take_screenshot(self, filename: Optional[str] = None) -> bool:
        """Take a screenshot"""
        try:
            from PIL import ImageGrab
            from datetime import datetime
            
            if not filename:
                desktop = Path.home() / "Desktop"
                filename = desktop / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def empty_recycle_bin(self) -> bool:
        """Empty the recycle bin"""
        try:
            import winshell
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            logger.info("Emptied recycle bin")
            return True
        except Exception as e:
            logger.error(f"Failed to empty recycle bin: {e}")
            return False
    
    def get_startup_programs(self) -> List[str]:
        """Get list of startup programs"""
        try:
            import winreg
            programs = []
            
            reg_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
            ]
            
            for hkey, path in reg_paths:
                try:
                    key = winreg.OpenKey(hkey, path)
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            programs.append(f"{name}: {value}")
                            i += 1
                        except WindowsError:
                            break
                    winreg.CloseKey(key)
                except Exception:
                    continue
            
            return programs
        except Exception as e:
            logger.error(f"Failed to get startup programs: {e}")
            return []
    
    def set_wallpaper(self, image_path: str) -> bool:
        """Set desktop wallpaper"""
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            logger.info(f"Set wallpaper: {image_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to set wallpaper: {e}")
            return False
    
    def enable_dark_mode(self, enable: bool = True) -> bool:
        """Enable or disable Windows dark mode"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                0,
                winreg.KEY_SET_VALUE
            )
            
            value = 0 if enable else 1
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            
            logger.info(f"{'Enabled' if enable else 'Disabled'} dark mode")
            return True
        except Exception as e:
            logger.error(f"Failed to toggle dark mode: {e}")
            return False
    
    def get_wifi_networks(self) -> List[str]:
        """Get available WiFi networks"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "networks"],
                capture_output=True,
                text=True
            )
            
            networks = []
            for line in result.stdout.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(":")[1].strip()
                    if ssid:
                        networks.append(ssid)
            
            return networks
        except Exception as e:
            logger.error(f"Failed to get WiFi networks: {e}")
            return []
    
    def connect_wifi(self, ssid: str, password: str) -> bool:
        """Connect to a WiFi network"""
        try:
            # Create profile XML
            profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
            
            # Save profile
            profile_path = Path.home() / f"{ssid}_profile.xml"
            with open(profile_path, 'w') as f:
                f.write(profile)
            
            # Add profile
            subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_path}"])
            
            # Connect
            subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"])
            
            # Clean up
            profile_path.unlink()
            
            logger.info(f"Connected to WiFi: {ssid}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to WiFi: {e}")
            return False


class PowerManager:
    """Manage power and sleep settings"""
    
    @staticmethod
    def set_sleep_timer(minutes: int) -> bool:
        """Set system to sleep after specified minutes"""
        try:
            seconds = minutes * 60
            subprocess.run(["powercfg", "/change", "standby-timeout-ac", str(minutes)])
            logger.info(f"Set sleep timer to {minutes} minutes")
            return True
        except Exception as e:
            logger.error(f"Failed to set sleep timer: {e}")
            return False
    
    @staticmethod
    def prevent_sleep(enable: bool = True) -> bool:
        """Prevent system from sleeping"""
        try:
            if enable:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
            else:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # ES_CONTINUOUS
            
            logger.info(f"{'Enabled' if enable else 'Disabled'} sleep prevention")
            return True
        except Exception as e:
            logger.error(f"Failed to manage sleep prevention: {e}")
            return False
    
    @staticmethod
    def hibernate() -> bool:
        """Put system into hibernate"""
        try:
            subprocess.run(["shutdown", "/h"])
            return True
        except Exception as e:
            logger.error(f"Failed to hibernate: {e}")
            return False


from pathlib import Path
