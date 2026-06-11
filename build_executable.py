"""
Build script to create a standalone executable for the Folder Monitor.
This bundles Python, dependencies, and pngquant into a single distributable folder.
"""
import PyInstaller.__main__
import sys
import shutil
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent

# Path to pngquant executable
pngquant_path = script_dir / "pngquant" / "pngquant.exe"

# Build arguments for PyInstaller
pyinstaller_args = [
    str(script_dir / "monitor_folder.py"),  # Main script
    "--name=FolderMonitor",                  # Name of the executable
    "--onedir",                              # Create a folder with all files
    "--console",                             # Show console window
    "--icon=NONE",                           # No icon (you can add one later)
    "--clean",                               # Clean PyInstaller cache and remove temporary files
    "--noconfirm",                           # Replace output directory without asking
]

# Add pngquant if it exists
if pngquant_path.exists():
    print(f"✓ Found pngquant at: {pngquant_path}")
    pyinstaller_args.append(f"--add-binary={pngquant_path};pngquant")
else:
    print(f"⚠ Warning: pngquant not found at {pngquant_path}")
    print("  The executable will still work but compression will require pngquant to be installed separately")

# Optionally add OptiPNG if available
optipng_path = script_dir / "optipng" / "optipng.exe"
if optipng_path.exists():
    print(f"✓ Found optipng at: {optipng_path}")
    pyinstaller_args.append(f"--add-binary={optipng_path};optipng")

print("\nBuilding executable...")
print("Arguments:", pyinstaller_args)

# Run PyInstaller
PyInstaller.__main__.run(pyinstaller_args)

# Post-build: Copy config.json to the dist folder (next to exe)
dist_folder = script_dir / "dist" / "FolderMonitor"
config_template = script_dir / "config.json"

# Check if dist folder exists
if dist_folder.exists():
    print(f"\n✓ Build output found at: {dist_folder}")
    
    if config_template.exists():
        # Create a clean config template for distribution (remove personal paths)
        import json
        import re as _re

        def _strip_json_comments(text):
            """Strip // and /* */ comments from JSONC text, preserving strings."""
            result, i, n = [], 0, len(text)
            while i < n:
                if text[i] == '"':
                    result.append('"')
                    i += 1
                    while i < n:
                        ch = text[i]; result.append(ch); i += 1
                        if ch == '\\' and i < n: result.append(text[i]); i += 1
                        elif ch == '"': break
                elif text[i] == '/' and i+1 < n and text[i+1] == '/':
                    i += 2
                    while i < n and text[i] != '\n': i += 1
                elif text[i] == '/' and i+1 < n and text[i+1] == '*':
                    i += 2
                    while i < n and not (text[i] == '*' and i+1 < n and text[i+1] == '/'): i += 1
                    i += 2
                else: result.append(text[i]); i += 1
            return ''.join(result)

        with open(config_template, 'r', encoding='utf-8') as f:
            config_data = json.loads(_strip_json_comments(f.read()))
        
        # Create template config with example paths
        template_config = {
            "source_folders": ["C:/path/to/your/source/folder"],
            "destination_folder": "C:/path/to/your/destination/folder",
            "ignore_extensions": config_data.get("ignore_extensions", [".txt", ".bak", ".bak.png"]),
            "ignore_files_without_extension": config_data.get("ignore_files_without_extension", True),
            "cooldown": config_data.get("cooldown", 3.0),
            "compress_png": config_data.get("compress_png", True),
            "parse_filename_paths": config_data.get("parse_filename_paths", True),
            "filename_path_delimiter": config_data.get("filename_path_delimiter", "§"),
            "parse_resize_from_filename": config_data.get("parse_resize_from_filename", True),
            "resize_filter": config_data.get("resize_filter", "mitchell"),
            "resize_sharpen": config_data.get("resize_sharpen", False),
            "skip_compression_prefix_enabled": config_data.get("skip_compression_prefix_enabled", True),
            "skip_compression_prefix": config_data.get("skip_compression_prefix", "#"),
            "path_macros": {
                "UI": "C:/path/to/your/secondary/destination/folder"
            },
            "debug": False
        }
        
        with open(dist_folder / "config.json", 'w', encoding='utf-8') as f:
            json.dump(template_config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Created config.json template at {dist_folder / 'config.json'}")
    else:
        print(f"⚠ Warning: config.json template not found at {config_template}")
else:
    print(f"\n✗ ERROR: Build folder not found at {dist_folder}")
    print("PyInstaller may have failed. Check the output above for errors.")

print("\n" + "=" * 60)
print("Build complete!")
print("=" * 60)
print(f"\nExecutable location: {script_dir / 'dist' / 'FolderMonitor'}")
print("\nNext steps:")
print("1. Copy the 'dist/FolderMonitor' folder to share with your team")
print("2. Edit config.json in that folder with your paths")
print("3. Run FolderMonitor.exe to start monitoring")
print("\nNote: config.json will be editable - each user can customize their paths!")

# Pause before closing if run by double-clicking
input("\nPress Enter to close...")
