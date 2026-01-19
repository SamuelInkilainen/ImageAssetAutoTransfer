# Folder Monitor Script - version 1.3

A Python script that monitors a specified folder (including subfolders) for file changes and automatically copies modified files to a destination folder.

## Features

- **Real-time Monitoring**: Watches for file changes in real-time
- **Recursive Monitoring**: Monitors all subfolders automatically
- **Automatic Copying**: Copies modified or newly created files immediately
- **Folder Structure Preservation**: Maintains the same folder structure in the destination
- **Easy Configuration**: Simple JSON configuration file for folder paths
- **Cross-platform**: Works on Windows, macOS, and Linux
- **PNG Compression**: Optional pngquant compression for PNG files
- **Image Resizing**: Optional ImageMagick-based image resizing parsed from filename
- **Filename Path Parsing**: Extract subfolder paths from filenames for organized output
- **File Filtering**: Ignore specific file extensions (including multi-part extensions like `.bak.png`)

## Installation

1. Install Python 3.7 or higher if not already installed
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Edit the `config.json` file to set your source and destination folders.

### Single Source Folder (simple):

```json
{
  "source_folder": "C:\\Path\\To\\Source\\Folder",
  "destination_folder": "C:\\Path\\To\\Destination\\Folder"
}
```

### Multiple Source Folders:

```json
{
  "source_folders": [
    {
      "label": "Project Assets",
      "path": "C:\\Path\\To\\First\\Source"
    },
    {
      "label": "Backup Files",
  ],
  "destination_folder": "C:\\Path\\To\\Destination\\Folder",
  "ignore_extensions": [".txt", ".tmp", ".log"],
  "compress_png": true
} "destination_folder": "C:\\Path\\To\\Destination\\Folder",
  "ignore_extensions": [".txt", ".tmp", ".log"]
}
```

You can also omit labels:

```json
{
  "source_folders": [
    "C:\\Path\\To\\First\\Source",
    "C:\\Path\\To\\Second\\Source"
  ],
  "destination_folder": "C:\\Path\\To\\Destination\\Folder"
}
```
**Note**: You can use either single backslashes (`\`), double backslashes (`\\`), or forward slashes (`/`) in paths - Python will handle them all correctly.

### Optional Configuration Fields

- **`ignore_extensions`**: Array of file extensions to ignore (e.g., `["txt", ".tmp", ".log", ".bak.png"]`)
- **`compress_png`**: Set to `true` to enable PNG compression using pngquant (default: `false`)
- **`pngquant_path`**: Full path to pngquant executable (optional, defaults to `pngquant` in PATH)
- **`parse_filename_paths`**: Set to `true` to parse subfolder paths from filenames (default: `false`)
- **`filename_path_delimiter`**: Character used to separate path parts in filenames (default: `"§"`)
- **`parse_resize_from_filename`**: Set to `true` to parse resize percentage from filenames (default: `false`)

## PNG Compression

The script uses a **TinyPNG-like multi-pass compression** approach for optimal file size and quality:

**Pass 1: Lossy Compression (pngquant)**
- Aggressive color quantization with quality range 60-85%
- Posterization to reduce color precision
- Metadata stripping for smaller files

**Pass 2: Lossless Optimization (OptiPNG/AdvPNG)** 
- Additional PNG structure optimization
- Fallback to AdvPNG if OptiPNG not available

This approach typically achieves **70-80% file size reduction** while preserving visual quality, comparable to TinyPNG.

### Setup:

1. **Install pngquant** (required):
   - Download from [pngquant.org](https://pngquant.org/)
   - Or install via package manager:
     - Windows: `choco install pngquant`
     - macOS: `brew install pngquant`
     - Linux: `apt install pngquant`

2. **Install OptiPNG** (recommended for best results):
   - Download from [optipng.sourceforge.net](http://optipng.sourceforge.net/)
   - Or install via package manager:
     - Windows: `choco install optipng`
     - macOS: `brew install optipng`
     - Linux: `apt install optipng`

3. **Configure in config.json**:
   ```json
   {
     "compress_png": true,
     "pngquant_path": "C:\\Program Files\\pngquant\\pngquant.exe",
     "optipng_path": "C:\\Program Files\\OptiPNG\\optipng.exe"
   }
   ```

   Or if both are in your system PATH:
   ```json
   {
     "compress_png": true
   }
   ```

The script uses quality 80-95 for compression. PNG files are copied first, then compressed in place at the destination.

## Image Resizing with ImageMagick

To enable automatic image resizing based on filename:

1. Install ImageMagick:
   - **Windows**: Download from [imagemagick.org](https://imagemagick.org/script/download.php)
   - **macOS**: `brew install imagemagick`
   - **Linux**: `sudo apt-get install imagemagick`

2. Enable in your config:
   ```json
   {
     "parse_resize_from_filename": true
   }
   ```

3. Name your files with resize percentage at the start:
   - `50% image1.png` → Resizes to 50% of original size
   - `25% subfolder1#image2.png` → Resizes to 25% and saves to subfolder1/

**Processing Order**: Copy → Resize (if enabled) → Compress (if enabled)

## Filename Path Parsing

Organize files into subfolders by encoding paths in filenames:

1. Enable in your config:
   ```json
   {
     "parse_filename_paths": true,
     "filename_path_delimiter": "#"
   }
   ```

2. Use the delimiter to specify subfolder paths:
   - `subfolder1#image.png` → Saved to `destination/subfolder1/image.png`
   - `ui#buttons#save.png` → Saved to `destination/ui/buttons/save.png`

3. Combine with resize:
   - `50% subfolder1#image.png` → Resized to 50%, saved to `destination/subfolder1/image.png`

**Note**: You can use any delimiter character that's valid in filenames (e.g., `#`, `§`, `~`, etc.)

**Note**: You can use either single backslashes (`\`), double backslashes (`\\`), or forward slashes (`/`) in paths - Python will handle them all correctly.

### Configuration Examples

**Windows:**
```json
{
  "source_folder": "C:\\Users\\YourName\\Documents\\ProjectAssets",
  "destination_folder": "D:\\Backup\\ProjectAssets"
}
```

**macOS/Linux:**
```json
{
  "source_folder": "/Users/YourName/Documents/ProjectAssets",
  "destination_folder": "/Volumes/Backup/ProjectAssets"
}
```

## Usage

1. Configure your folders in `config.json`
2. Run the script:

```bash
python monitor_folder.py
```

3. The script will start monitoring and display:
   - Source folder being monitored
   - Destination folder for copies
   - Real-time updates when files are copied

4. Press `Ctrl+C` to stop monitoring

## How It Works

- The script uses the `watchdog` library to monitor file system events
- When a file is created or modified in the source folder:
  - The file is automatically copied to the destination folder
  - The relative folder structure is preserved
  - Existing files are replaced with newer versions
- All subfolders are monitored recursively

## Troubleshooting

### "config.json not found" error
- Make sure `config.json` is in the same directory as `monitor_folder.py`

### "Source folder does not exist" error
- Check that the path in `config.json` is correct
- Ensure the folder exists before running the script

### Files not copying
- Check file permissions for both source and destination folders
- Ensure destination folder is writable

## Requirements

- Python 3.7+
- watchdog 3.0.0
- ImageMagick (optional, for image resizing)
- pngquant (optional, for PNG compression)

## License

This project is provided as-is for personal or commercial use.
