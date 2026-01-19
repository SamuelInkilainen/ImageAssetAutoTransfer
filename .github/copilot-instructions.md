<!-- Workspace-specific Copilot instructions -->

## Project Overview
This is a Python script project that monitors a specified folder (including subfolders) for file changes and automatically copies modified files to a destination folder.

## Project Structure
- `monitor_folder.py`: Main script that monitors folder changes
- `config.json`: Configuration file for source and destination paths
- `requirements.txt`: Python dependencies

## Key Features
- Real-time folder monitoring using watchdog library
- Recursive subfolder monitoring
- Automatic file copying on changes
- Easy configuration via JSON file
- Supports file creation, modification, and deletion tracking

## Development Guidelines
- Keep the configuration file simple and user-friendly
- Use Python's pathlib for cross-platform path handling
- Include proper error handling for file operations
- Log important events for debugging purposes
