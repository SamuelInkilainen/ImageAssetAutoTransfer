import json
import sys
import time
import shutil
import subprocess
import re
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

class FolderMonitorHandler(FileSystemEventHandler):
    """Handles file system events and copies changed files to destination."""
    
    def __init__(self, source_path, destination_path, label=None, ignore_extensions=None, ignore_files_without_extension=False, processing_delay=0, compress_png=False, pngquant_path=None, optipng_path=None, debug=False, parse_filename_paths=False, filename_path_delimiter='§', parse_resize_from_filename=False, path_macros=None):
        self.source_path = Path(source_path).resolve()
        self.destination_path = Path(destination_path).resolve()
        self.label = label or str(self.source_path)
        self.ignore_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in (ignore_extensions or [])]
        self.ignore_files_without_extension = ignore_files_without_extension
        self.processing_delay = processing_delay
        self.compress_png = compress_png
        
        # Auto-detect bundled pngquant if running as executable
        if pngquant_path:
            self.pngquant_path = pngquant_path
        else:
            # Check for bundled pngquant in PyInstaller bundle
            if getattr(sys, 'frozen', False):
                # PyInstaller stores bundled files in sys._MEIPASS
                bundle_dir = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
                bundled_pngquant = bundle_dir / 'pngquant' / 'pngquant.exe'
                if bundled_pngquant.exists():
                    self.pngquant_path = str(bundled_pngquant)
                else:
                    self.pngquant_path = 'pngquant'  # Fall back to PATH
            else:
                self.pngquant_path = 'pngquant'  # Default to PATH
        
        # Auto-detect bundled optipng if running as executable
        if optipng_path:
            self.optipng_path = optipng_path
        else:
            # Check for bundled optipng in PyInstaller bundle
            if getattr(sys, 'frozen', False):
                # PyInstaller stores bundled files in sys._MEIPASS
                bundle_dir = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
                bundled_optipng = bundle_dir / 'optipng' / 'optipng.exe'
                if bundled_optipng.exists():
                    self.optipng_path = str(bundled_optipng)
                else:
                    self.optipng_path = 'optipng'  # Fall back to PATH
            else:
                self.optipng_path = 'optipng'  # Default to PATH
        
        self.debug = debug
        self.parse_filename_paths = parse_filename_paths
        self.filename_path_delimiter = filename_path_delimiter
        self.parse_resize_from_filename = parse_resize_from_filename
        self.path_macros = path_macros or {}
        self._recently_processed = {}
        
        # Show configuration info on startup
        print(f"[{self.label}]")
        print(f"  Monitoring: {self.source_path}")
        print(f"  Copying to: {self.destination_path}")
        if self.ignore_extensions:
            print(f"  Ignoring: {', '.join(self.ignore_extensions)}")
        if self.ignore_files_without_extension:
            print(f"  Ignoring files without extension: Enabled")
        if self.processing_delay > 0:
            print(f"  Processing Delay: {self.processing_delay}s")
        if self.compress_png:
            print(f"  PNG Compression: Enabled (quality 90-100)")
        if self.parse_filename_paths:
            print(f"  Filename Path Parsing: Enabled (delimiter: '{self.filename_path_delimiter}')")
        if self.parse_resize_from_filename:
            print(f"  Resize from Filename: Enabled")
        if self.path_macros:
            print(f"  Path Macros:")
            for macro, expansion in self.path_macros.items():
                print(f"    {macro} → {expansion}")
        if self.debug:
            print(f"  Debug Mode: Enabled")
        print("-" * 50)
    
    def copy_file(self, src_path):
        """Copy a file from source to destination, preserving folder structure."""
        try:
            src_file = Path(src_path)
                        # Deduplicate rapid events (watchdog fires both created and modified)
            now = time.time()
            last_time = self._recently_processed.get(str(src_file))
            if last_time and (now - last_time) < (self.processing_delay + 1.0):
                if self.debug:
                    print(f"  Skipping duplicate event for {src_file.name}")
                return
            self._recently_processed[str(src_file)] = now
                        # Show file detection
            print(f"\n→ Detected: {src_file.name}")
            
            # Wait for file to stabilize (application may delete+recreate during save)
            if self.processing_delay > 0:
                if self.debug:
                    print(f"  Waiting for file to stabilize...")
                prev_stat = None
                max_attempts = int(10 / self.processing_delay)  # Max ~10 seconds
                for attempt in range(max_attempts):
                    time.sleep(self.processing_delay)
                    
                    if not src_file.exists():
                        if self.debug:
                            print(f"  File no longer exists (likely a temp file) - skipping")
                        self._recently_processed.pop(str(src_file), None)
                        return
                    
                    try:
                        stat = src_file.stat()
                        current_stat = (stat.st_size, stat.st_mtime)
                    except OSError:
                        if self.debug:
                            print(f"  File became inaccessible - skipping")
                        self._recently_processed.pop(str(src_file), None)
                        return
                    
                    if prev_stat == current_stat:
                        if self.debug:
                            print(f"  File stable after {(attempt + 1) * self.processing_delay:.2f}s")
                        break
                    prev_stat = current_stat
                else:
                    if self.debug:
                        print(f"  Warning: File did not stabilize within timeout, processing anyway")
            
            # Check if files without extensions should be ignored
            if self.ignore_files_without_extension and not src_file.suffix:
                if self.debug:
                    print(f"  Skipping file without extension")
                return
            
            # Check if file extension should be ignored
            if self.ignore_extensions:
                # Check both single extension and multi-part extensions (e.g., .bak.png)
                if src_file.suffix.lower() in self.ignore_extensions:
                    if self.debug:
                        print(f"[DEBUG] Ignoring {src_file.name} (extension {src_file.suffix})")
                    return  # Skip ignored file types
                # Check for multi-part extensions
                for ext in self.ignore_extensions:
                    if src_file.name.lower().endswith(ext.lower()):
                        if self.debug:
                            print(f"[DEBUG] Ignoring {src_file.name} (extension {ext})")
                        return  # Skip ignored file types
            
            # Calculate relative path from source folder
            relative_path = src_file.relative_to(self.source_path)
            
            # Variables for resize and filename parsing
            resize_percentage = None
            filename = src_file.name
            
            # Parse resize percentage from filename if enabled
            if self.parse_resize_from_filename:
                # Match pattern like "50% " at the start of filename
                resize_match = re.match(r'^(\d+)%\s+(.+)$', filename)
                if resize_match:
                    resize_percentage = int(resize_match.group(1))
                    filename = resize_match.group(2)  # Remove the percentage prefix
                    
                    # Delete old scale variations of the same base filename from source folder
                    src_dir = src_file.parent
                    for sibling in src_dir.iterdir():
                        if sibling == src_file or sibling.is_dir():
                            continue
                        sibling_match = re.match(r'^(\d+)%\s+(.+)$', sibling.name)
                        if sibling_match and sibling_match.group(2) == filename:
                            try:
                                sibling.unlink()
                                print(f"  Deleted old variation: {sibling.name}")
                                if self.debug:
                                    print(f"[DEBUG] Removed old scale variation {sibling_match.group(1)}% from source")
                            except Exception as e:
                                print(f"{Colors.YELLOW}  Warning: Could not delete old variation {sibling.name}: {e}{Colors.RESET}")
            
            # Parse filename paths if enabled
            if self.parse_filename_paths:
                # Check if delimiter exists in filename
                if self.filename_path_delimiter in filename:
                    # Split filename by delimiter to get path parts
                    parts = filename.split(self.filename_path_delimiter)
                    
                    # Last part is the actual filename, everything before is the path
                    actual_filename = parts[-1]
                    subfolder_parts = parts[:-1]
                    
                    # Check if first path segment matches a path macro
                    if subfolder_parts and subfolder_parts[0] in self.path_macros:
                        macro_name = subfolder_parts[0]
                        macro_path = Path(self.path_macros[macro_name])
                        remaining_parts = subfolder_parts[1:]
                        
                        if remaining_parts:
                            dest_file = macro_path / Path(*remaining_parts) / actual_filename
                        else:
                            dest_file = macro_path / actual_filename
                        
                        if self.debug:
                            print(f"  Path macro: {macro_name} → {macro_path}")
                    else:
                        # Create the subfolder path
                        subfolder_path = Path(*subfolder_parts) if subfolder_parts else Path()
                        
                        # Combine with relative directory path (excluding filename)
                        relative_dir = relative_path.parent
                        if relative_dir != Path('.'):
                            # File is in a subdirectory of source, preserve that structure
                            dest_file = self.destination_path / relative_dir / subfolder_path / actual_filename
                        else:
                            # File is in root of source folder
                            dest_file = self.destination_path / subfolder_path / actual_filename
                else:
                    # No delimiter in filename, use normal behavior
                    dest_file = self.destination_path / relative_path
            else:
                # Normal behavior: preserve folder structure
                dest_file = self.destination_path / relative_path
            
            if self.debug:
                print(f"[DEBUG] Resolved destination: {dest_file}")
            
            # Create destination directory if it doesn't exist
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(src_file, dest_file)
            
            # Resize image if percentage was parsed from filename
            if resize_percentage is not None and dest_file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                try:
                    # Use ImageMagick to resize the image
                    # Try 'magick' command first (ImageMagick 7+), fall back to 'convert' (ImageMagick 6)
                    resize_arg = f"{resize_percentage}%"
                    
                    # Try ImageMagick 7+ syntax first
                    try:
                        result = subprocess.run(
                            ['magick', str(dest_file), '-resize', resize_arg, str(dest_file)],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            print(f"  Resized to {resize_percentage}%")
                        else:
                            raise subprocess.CalledProcessError(result.returncode, 'magick')
                    except (FileNotFoundError, subprocess.CalledProcessError):
                        # Fall back to ImageMagick 6 'convert' command
                        result = subprocess.run(
                            ['convert', str(dest_file), '-resize', resize_arg, str(dest_file)],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            print(f"  Resized to {resize_percentage}%")
                        else:
                            print(f"{Colors.YELLOW}  Warning: Failed to resize image{Colors.RESET}")
                except FileNotFoundError:
                    print(f"{Colors.YELLOW}  Warning: ImageMagick not found. Please install ImageMagick to use resize feature.{Colors.RESET}")
                except subprocess.TimeoutExpired:
                    print(f"{Colors.YELLOW}  Warning: Image resize timeout{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.YELLOW}  Warning: Failed to resize image: {str(e)}{Colors.RESET}")
            
            # Compress PNG files if enabled (TinyPNG-like multi-pass approach)
            if self.compress_png and src_file.suffix.lower() == '.png':
                try:
                    # Get original file size for comparison
                    original_size = dest_file.stat().st_size
                    pngquant_success = False
                    
                    if self.debug:
                        print(f"\n[DEBUG] Starting compression for {relative_path}")
                        print(f"[DEBUG] Original size: {original_size:,} bytes")
                    
                    # PASS 1: pngquant - prioritize quality over compression
                    try:
                        if self.debug:
                            print(f"[DEBUG] Running pngquant...")
                        
                        # High-quality settings: Prioritize visual fidelity, target ~40-50% reduction
                        pngquant_command = [
                            self.pngquant_path,
                            '--force',              # Overwrite existing files
                            '--ext', '.png',        # Replace original file
                            '--quality', '90-100',  # Very high quality - preserve maximum visual fidelity
                            '--speed', '1',         # Best quality algorithm
                            '--strip',              # Remove metadata (small gain, no quality loss)
                            str(dest_file)
                        ]
                        
                        if self.debug:
                            print(f"[DEBUG] Command: {' '.join(pngquant_command)}")
                        
                        result = subprocess.run(
                            pngquant_command,
                            capture_output=True,
                            text=True,
                            timeout=90
                        )
                        pngquant_success = (result.returncode == 0)
                        
                        if self.debug:
                            if pngquant_success:
                                size_after_pngquant = dest_file.stat().st_size
                                pngquant_reduction = ((original_size - size_after_pngquant) / original_size * 100)
                                print(f"[DEBUG] pngquant SUCCESS: {size_after_pngquant:,} bytes ({pngquant_reduction:.1f}% reduction)")
                            else:
                                print(f"[DEBUG] pngquant FAILED: return code {result.returncode}")
                                if result.stderr:
                                    print(f"[DEBUG] Error output: {result.stderr}")
                                    
                    except FileNotFoundError:
                        try:
                            display_path = dest_file.relative_to(self.destination_path)
                        except ValueError:
                            display_path = dest_file
                        print(f"  Copied to: {display_path}")
                        print(f"{Colors.YELLOW}  Compression: Failed (pngquant not found){Colors.RESET}")
                        print(f"  Install pngquant: https://pngquant.org/")
                        self.compress_png = False
                        pngquant_success = False
                    
                    # PASS 2: OptiPNG/AdvPNG for lossless optimization (TinyPNG does this too)
                    if pngquant_success:
                        size_before_optipng = dest_file.stat().st_size
                        optipng_success = False
                        
                        if self.debug:
                            print(f"[DEBUG] Running OptiPNG...")
                        
                        # Try OptiPNG first (more common)
                        try:
                            optipng_result = subprocess.run(
                                [self.optipng_path, '-o7', '-zm1-9', '-strip', 'all', str(dest_file)],
                                capture_output=True,
                                text=True,
                                timeout=60,
                                check=False  # Don't raise on non-zero exit
                            )
                            optipng_success = (optipng_result.returncode == 0)
                            
                            if self.debug:
                                if optipng_success:
                                    size_after_optipng = dest_file.stat().st_size
                                    optipng_reduction = ((size_before_optipng - size_after_optipng) / size_before_optipng * 100)
                                    print(f"[DEBUG] OptiPNG SUCCESS: {size_after_optipng:,} bytes ({optipng_reduction:.1f}% additional reduction)")
                                else:
                                    print(f"[DEBUG] OptiPNG FAILED: return code {optipng_result.returncode}")
                                    
                        except FileNotFoundError:
                            if self.debug:
                                print(f"[DEBUG] OptiPNG not found, trying AdvPNG...")
                            
                            # OptiPNG not found, try advpng as alternative
                            try:
                                advpng_result = subprocess.run(
                                    ['advpng', '-z', '-4', str(dest_file)],
                                    capture_output=True,
                                    text=True,
                                    timeout=60,
                                    check=False
                                )
                                
                                if self.debug:
                                    if advpng_result.returncode == 0:
                                        size_after_advpng = dest_file.stat().st_size
                                        advpng_reduction = ((size_before_optipng - size_after_advpng) / size_before_optipng * 100)
                                        print(f"[DEBUG] AdvPNG SUCCESS: {size_after_advpng:,} bytes ({advpng_reduction:.1f}% additional reduction)")
                                    else:
                                        print(f"[DEBUG] AdvPNG FAILED: return code {advpng_result.returncode}")
                                        
                            except FileNotFoundError:
                                if self.debug:
                                    print(f"[DEBUG] AdvPNG not found - skipping pass 2 optimization")
                    
                    # Calculate final compression ratio and display results
                    try:
                        display_path = dest_file.relative_to(self.destination_path)
                    except ValueError:
                        display_path = dest_file
                    print(f"  Copied to: {display_path}")
                    
                    if pngquant_success:
                        compressed_size = dest_file.stat().st_size
                        reduction = ((original_size - compressed_size) / original_size * 100)
                        
                        if self.debug:
                            print(f"[DEBUG] FINAL: {compressed_size:,} bytes (total {reduction:.1f}% reduction)\n")
                        
                        if reduction > 0:
                            print(f"  Compression: {Colors.GREEN}✓ Success ({reduction:.1f}% reduction){Colors.RESET}")
                        else:
                            print(f"  Compression: Skipped (already optimized)")
                    else:
                        print(f"  Compression: Skipped (quality threshold not met)")
                        print(f"  {Colors.GREEN}✓ Success{Colors.RESET}")
                        
                except subprocess.TimeoutExpired:
                    print(f"{Colors.YELLOW}  Compression: Timeout{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.YELLOW}  Compression: Error{Colors.RESET}")
            else:
                # Non-PNG file or compression disabled
                try:
                    display_path = dest_file.relative_to(self.destination_path)
                except ValueError:
                    display_path = dest_file
                print(f"  Copied to: {display_path}")
                print(f"  {Colors.GREEN}✓ Success{Colors.RESET}")
            
            # Update dedup timestamp after processing to prevent re-processing
            # (processing can take longer than the dedup window)
            self._recently_processed[str(src_file)] = time.time()
            
        except Exception as e:
            print(f"  {Colors.RED}✗ Failed: {str(e)}{Colors.RESET}")
    
    def on_modified(self, event):
        """Called when a file is modified."""
        if not event.is_directory:
            if self.debug:
                print(f"[{self.label}] Modified: {event.src_path}")
            self.copy_file(event.src_path)
    
    def on_created(self, event):
        """Called when a file is created."""
        if not event.is_directory:
            if self.debug:
                print(f"[{self.label}] Created: {event.src_path}")
            self.copy_file(event.src_path)

def load_config():
    """Load configuration from config.json file."""
    # When running as executable, use the exe's directory
    # When running as script, use the script's directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = Path(sys.executable).parent
    else:
        # Running as script
        application_path = Path(__file__).parent
    
    config_path = application_path / "config.json"
    
    if not config_path.exists():
        print(f"{Colors.RED}Error: config.json not found!{Colors.RESET}")
        print(f"Expected location: {config_path}")
        print(f"\nPlease create a config.json file with your source and destination folders.")
        print(f"See the README.md for configuration examples.")
        
        # Pause if running as executable
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to close...")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate required fields - support both single and multiple source folders
        if 'destination_folder' not in config:
            print(f"{Colors.RED}Error: config.json must contain 'destination_folder'{Colors.RESET}")
            print(f"\nPlease add a destination_folder to your config.json")
            
            # Pause if running as executable
            if getattr(sys, 'frozen', False):
                input("\nPress Enter to close...")
            return None
        
        if 'source_folder' not in config and 'source_folders' not in config:
            print(f"{Colors.RED}Error: config.json must contain either 'source_folder' or 'source_folders'{Colors.RESET}")
            print(f"\nPlease add a source folder to your config.json")
            
            # Pause if running as executable
            if getattr(sys, 'frozen', False):
                input("\nPress Enter to close...")
            return None
        
        return config
    
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error parsing config.json: {str(e)}{Colors.RESET}")
        print(f"\nPlease check your config.json for syntax errors.")
        print(f"Make sure all quotes and commas are correct.")
        
        # Pause if running as executable
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to close...")
        return None
    except Exception as e:
        print(f"{Colors.RED}Error reading config.json: {str(e)}{Colors.RESET}")
        
        # Pause if running as executable
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to close...")
        return None

def main():
    """Main function to start folder monitoring."""
    print("=" * 50)
    print("Folder Monitor - Starting...")
    print("=" * 50)
    
    # Show config file location
    if getattr(sys, 'frozen', False):
        config_location = Path(sys.executable).parent / "config.json"
        print(f"\n{Colors.YELLOW}Configure your settings in: config.json{Colors.RESET}")
        print(f"(Located next to FolderMonitor.exe)\n")
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    destination_folder = Path(config['destination_folder'])
    
    # Create destination folder if it doesn't exist
    destination_folder.mkdir(parents=True, exist_ok=True)
    
    # Get source folders (support both single and multiple)
    source_folders = []
    if 'source_folders' in config:
        # Multiple source folders
        for item in config['source_folders']:
            if isinstance(item, dict):
                source_folders.append(item)
            else:
                # String path, create dict with no label
                source_folders.append({'path': item})
    elif 'source_folder' in config:
        # Single source folder (backward compatibility)
        source_folders.append({'path': config['source_folder']})
    
    # Validate all source paths
    for item in source_folders:
        source_path = Path(item['path'])
        if not source_path.exists():
            print(f"{Colors.RED}Error: Source folder does not exist: {source_path}{Colors.RESET}")
            print(f"\nPlease update the source folder path in config.json")
            if getattr(sys, 'frozen', False):
                config_location = Path(sys.executable).parent / "config.json"
                print(f"Config file location: {config_location}")
            
            # Pause if running as executable
            if getattr(sys, 'frozen', False):
                input("\nPress Enter to close...")
            return
        if not source_path.is_dir():
            print(f"{Colors.RED}Error: Source path is not a directory: {source_path}{Colors.RESET}")
            print(f"\nPlease update the source folder path in config.json")
            if getattr(sys, 'frozen', False):
                config_location = Path(sys.executable).parent / "config.json"
                print(f"Config file location: {config_location}")
            
            # Pause if running as executable
            if getattr(sys, 'frozen', False):
                input("\nPress Enter to close...")
            return
    
    # Set up the observer with all source folders
    observer = Observer()
    ignore_extensions = config.get('ignore_extensions', [])
    ignore_files_without_extension = config.get('ignore_files_without_extension', False)
    processing_delay = config.get('processing_delay', 0)
    compress_png = config.get('compress_png', False)
    pngquant_path = config.get('pngquant_path', None)
    optipng_path = config.get('optipng_path', None)
    debug = config.get('debug', False)
    parse_filename_paths = config.get('parse_filename_paths', False)
    filename_path_delimiter = config.get('filename_path_delimiter', '§')
    parse_resize_from_filename = config.get('parse_resize_from_filename', False)
    path_macros = config.get('path_macros', {})
    handlers = []
    for item in source_folders:
        source_path = Path(item['path'])
        label = item.get('label', None)
        event_handler = FolderMonitorHandler(source_path, destination_folder, label, ignore_extensions, ignore_files_without_extension, processing_delay, compress_png, pngquant_path, optipng_path, debug, parse_filename_paths, filename_path_delimiter, parse_resize_from_filename, path_macros)
        observer.schedule(event_handler, str(source_path), recursive=True)
        handlers.append(event_handler)
    
    # Start monitoring
    observer.start()
    print(f"\nMonitoring {len(source_folders)} folder(s). Press Ctrl+C to stop.")
    print(f"Type 'debug true' or 'debug false' to toggle debug output.\n")
    
    # Start console input listener for runtime commands
    def input_listener():
        while True:
            try:
                cmd = input().strip().lower()
                if cmd == 'debug true':
                    for h in handlers:
                        h.debug = True
                    print(f"{Colors.GREEN}Debug mode: Enabled{Colors.RESET}")
                elif cmd == 'debug false':
                    for h in handlers:
                        h.debug = False
                    print(f"{Colors.GREEN}Debug mode: Disabled{Colors.RESET}")
                elif cmd:
                    print(f"Unknown command: {cmd}")
            except EOFError:
                break
    
    listener_thread = threading.Thread(target=input_listener, daemon=True)
    listener_thread.start()
    
    try:
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("Stopping monitor...")
        observer.stop()
        observer.join()
        print("Monitor stopped.")
        print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Normal Ctrl+C exit, no need to pause
        pass
    except Exception as e:
        # Unexpected error - show it and pause
        print(f"\n{Colors.RED}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.RED}UNEXPECTED ERROR:{Colors.RESET}")
        print(f"{Colors.RED}{'=' * 50}{Colors.RESET}")
        print(f"{e}")
        import traceback
        traceback.print_exc()
        
        # Pause if running as executable so user can see the error
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to close...")
        raise
