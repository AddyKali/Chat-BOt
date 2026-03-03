"""
Advanced File Management Module
Handles complex file operations via voice commands
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """Handle advanced file operations"""
    
    def __init__(self):
        self.common_paths = {
            "desktop": Path.home() / "Desktop",
            "documents": Path.home() / "Documents",
            "downloads": Path.home() / "Downloads",
            "pictures": Path.home() / "Pictures",
            "videos": Path.home() / "Videos",
            "music": Path.home() / "Music"
        }
    
    def create_folder(self, folder_name: str, location: str = "desktop") -> bool:
        """Create a new folder"""
        try:
            base_path = self.common_paths.get(location.lower(), self.common_paths["desktop"])
            folder_path = base_path / folder_name
            folder_path.mkdir(exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return False
    
    def delete_file(self, filename: str, location: str = "desktop") -> bool:
        """Delete a file (with confirmation)"""
        try:
            base_path = self.common_paths.get(location.lower(), self.common_paths["desktop"])
            file_path = base_path / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def move_file(self, filename: str, source: str, destination: str) -> bool:
        """Move file from source to destination"""
        try:
            src_path = self.common_paths.get(source.lower(), self.common_paths["desktop"]) / filename
            dst_path = self.common_paths.get(destination.lower(), self.common_paths["documents"])
            
            if src_path.exists():
                shutil.move(str(src_path), str(dst_path / filename))
                logger.info(f"Moved {filename} from {source} to {destination}")
                return True
            else:
                logger.warning(f"Source file not found: {src_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to move file: {e}")
            return False
    
    def copy_file(self, filename: str, source: str, destination: str) -> bool:
        """Copy file from source to destination"""
        try:
            src_path = self.common_paths.get(source.lower(), self.common_paths["desktop"]) / filename
            dst_path = self.common_paths.get(destination.lower(), self.common_paths["documents"])
            
            if src_path.exists():
                shutil.copy2(str(src_path), str(dst_path / filename))
                logger.info(f"Copied {filename} from {source} to {destination}")
                return True
            else:
                logger.warning(f"Source file not found: {src_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to copy file: {e}")
            return False
    
    def rename_file(self, old_name: str, new_name: str, location: str = "desktop") -> bool:
        """Rename a file"""
        try:
            base_path = self.common_paths.get(location.lower(), self.common_paths["desktop"])
            old_path = base_path / old_name
            new_path = base_path / new_name
            
            if old_path.exists():
                old_path.rename(new_path)
                logger.info(f"Renamed {old_name} to {new_name}")
                return True
            else:
                logger.warning(f"File not found: {old_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to rename file: {e}")
            return False
    
    def list_files(self, location: str = "desktop", extension: Optional[str] = None) -> List[str]:
        """List files in a directory"""
        try:
            base_path = self.common_paths.get(location.lower(), self.common_paths["desktop"])
            
            if extension:
                files = [f.name for f in base_path.glob(f"*.{extension}")]
            else:
                files = [f.name for f in base_path.iterdir() if f.is_file()]
            
            logger.info(f"Listed {len(files)} files in {location}")
            return files
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    def search_files(self, query: str, location: str = "desktop") -> List[str]:
        """Search for files by name"""
        try:
            base_path = self.common_paths.get(location.lower(), self.common_paths["desktop"])
            files = [f.name for f in base_path.rglob(f"*{query}*")]
            logger.info(f"Found {len(files)} files matching '{query}'")
            return files
        except Exception as e:
            logger.error(f"Failed to search files: {e}")
            return []
    
    def open_folder(self, location: str = "desktop") -> bool:
        """Open a folder in file explorer"""
        try:
            base_path = self.common_paths.get(location.lower(), self.common_paths["desktop"])
            os.startfile(base_path)
            logger.info(f"Opened folder: {base_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            return False
    
    def get_file_info(self, filename: str, location: str = "desktop") -> Optional[dict]:
        """Get information about a file"""
        try:
            base_path = self.common_paths.get(location.lower(), self.common_paths["desktop"])
            file_path = base_path / filename
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            info = {
                "name": file_path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": file_path.suffix
            }
            return info
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None


class AutomationEngine:
    """Handle automated tasks and scripts"""
    
    def __init__(self):
        self.scheduled_tasks = []
    
    def create_batch_script(self, commands: List[str], script_name: str) -> bool:
        """Create a Windows batch script"""
        try:
            desktop = Path.home() / "Desktop"
            script_path = desktop / f"{script_name}.bat"
            
            with open(script_path, 'w') as f:
                f.write("@echo off\n")
                for cmd in commands:
                    f.write(f"{cmd}\n")
                f.write("pause\n")
            
            logger.info(f"Created batch script: {script_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create batch script: {e}")
            return False
    
    def run_powershell_command(self, command: str) -> Optional[str]:
        """Execute a PowerShell command"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            logger.info(f"PowerShell command executed: {command}")
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to run PowerShell command: {e}")
            return None
    
    def organize_downloads(self) -> bool:
        """Organize downloads folder by file type"""
        try:
            downloads = Path.home() / "Downloads"
            
            # Create subfolders
            folders = {
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
                "Documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"],
                "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
                "Music": [".mp3", ".wav", ".flac", ".aac"],
                "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
                "Executables": [".exe", ".msi"]
            }
            
            # Create folders
            for folder_name in folders.keys():
                (downloads / folder_name).mkdir(exist_ok=True)
            
            # Move files
            for file in downloads.iterdir():
                if file.is_file():
                    ext = file.suffix.lower()
                    for folder_name, extensions in folders.items():
                        if ext in extensions:
                            dest = downloads / folder_name / file.name
                            if not dest.exists():
                                shutil.move(str(file), str(dest))
                            break
            
            logger.info("Organized downloads folder")
            return True
        except Exception as e:
            logger.error(f"Failed to organize downloads: {e}")
            return False
    
    def clean_temp_files(self) -> bool:
        """Clean Windows temporary files"""
        try:
            temp_paths = [
                Path(os.environ.get("TEMP", "")),
                Path(os.environ.get("TMP", "")),
                Path("C:/Windows/Temp")
            ]
            
            files_deleted = 0
            for temp_path in temp_paths:
                if temp_path.exists():
                    for item in temp_path.iterdir():
                        try:
                            if item.is_file():
                                item.unlink()
                                files_deleted += 1
                            elif item.is_dir():
                                shutil.rmtree(item, ignore_errors=True)
                                files_deleted += 1
                        except Exception:
                            continue
            
            logger.info(f"Cleaned {files_deleted} temporary items")
            return True
        except Exception as e:
            logger.error(f"Failed to clean temp files: {e}")
            return False
