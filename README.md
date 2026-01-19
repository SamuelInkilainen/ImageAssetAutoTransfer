# Image Asset Auto-Transfer

A Python script that monitors specified folders (including subfolders) for file changes and automatically copies modified files to a destination folder. Perfect for game development workflows where assets need to be automatically synced between design tools and game project folders.

## Features

- **Real-time Monitoring**: Watches for file changes in real-time using the watchdog library
- **Recursive Monitoring**: Monitors all subfolders automatically
- **Automatic Copying**: Copies modified or newly created files immediately to destination
- **Folder Structure Preservation**: Maintains the same folder structure in the destination
- **Multi-Source Support**: Monitor multiple source folders simultaneously
- **File Filtering**: Ignore specific file extensions (supports multi-part extensions like `.bak.png`)
- **PNG Compression**: Optional high-quality PNG compression using pngquant (90-100% quality)
- **Image Resizing**: Parse resize percentage from filename (e.g., `50% image.png` resizes to 50%)
- **Filename Path Parsing**: Extract subfolder paths from filenames using a delimiter (e.g., `folder§subfolder§file.png`)
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Executable Version**: Can be built as a standalone executable (no Python required)

## Requirements

- Python 3.7 or higher
- watchdog library (for file monitoring)

### Optional Tools

- **pngquant** - For PNG compression (download from [pngquant.org](https://pngquant.org/))
- **ImageMagick** - For image resizing (download from [imagemagick.org](https://imagemagick.org/))

## Installation

### Standard Installation

1. Clone this repository:
```bash
git clone <your-repository-url>
cd ImageAssetAutoTransfer
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install pngquant for PNG compression
4. (Optional) Install ImageMagick for image resizing

### Building as Executable

If you want a standalone executable (no Python required):

```bash
python build_executable.py
```

The executable will be created in the `dist` folder. See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for details.

## Configuration

Edit the `config.json` file to configure the script for your needs.

### Basic Configuration (Single Source)

```json
{
  "source_folders": ["C:\\Path\\To\\Your\\Source\\Folder"],
  "destination_folder": "C:\\Path\\To\\Destination\\Folder"
}
```

### Full Configuration Example

```json
{
  "source_folders": [
    "C:\\Users\\You\\Projects\\GameAssets",
    "C:\\Users\\You\\Projects\\ExtraAssets"
  ],
  "destination_folder": "C:\\Users\\You\\GameProject\\Resources",
  "ignore_extensions": [".txt", ".bak", ".bak.png"],
  "compress_png": true,
  "parse_filename_paths": true,
  "filename_path_delimiter": "§",
  "parse_resize_from_filename": true,
  "pngquant_path": "C:\\Tools\\pngquant\\pngquant.exe",
  "debug": false
}
```

### Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `source_folders` | array | Yes | List of folder paths to monitor |
| `destination_folder` | string | Yes | Where files will be copied to |
| `ignore_extensions` | array | No | File extensions to ignore (e.g., `[".txt", ".bak.png"]`) |
| `compress_png` | boolean | No | Enable high-quality PNG compression (default: false) |
| `parse_filename_paths` | boolean | No | Extract folder paths from filenames (default: false) |
| `filename_path_delimiter` | string | No | Delimiter for filename paths (default: "§") |
| `parse_resize_from_filename` | boolean | No | Parse resize percentage from filename (default: false) |
| `pngquant_path` | string | No | Path to pngquant executable (auto-detected if bundled) |
| `debug` | boolean | No | Enable debug output (default: false) |

## Usage

### Running the Script

```bash
python monitor_folder.py
```

The script will:
1. Load configuration from `config.json`
2. Start monitoring all specified source folders
3. Display monitoring status for each folder
4. Continuously watch for file changes
5. Automatically copy/process changed files to the destination

**To stop monitoring**: Press `Ctrl+C`

### Using the Executable

If you built the executable version:

```bash
# Windows
cd dist\FolderMonitor
FolderMonitor.exe

# The executable must be in the same directory as config.json
```

## Advanced Features

### PNG Compression

The script uses high-quality PNG compression (90-100% quality) via pngquant:

- **Quality Settings**: 90-100% (prioritizes visual fidelity over maximum compression)
- **Compression Ratio**: Typically 40-50% file size reduction
- **Processing**: Files are copied first, then compressed at destination

**Requirements**: Install [pngquant](https://pngquant.org/)

### Image Resizing

Automatically resize images by adding a percentage prefix to the filename:

**Examples**:
- `50% character.png` → Resizes to 50% of original dimensions
- `25% background.jpg` → Resizes to 25% of original dimensions

**Requirements**: Install [ImageMagick](https://imagemagick.org/)

**Processing Order**: Copy → Resize → Compress (if PNG)

### Filename Path Parsing

Encode subfolder structure directly in filenames using a delimiter:

**Example with delimiter `§`**:
- `ui§buttons§save.png` → Saved to `destination/ui/buttons/save.png`
- `characters§player§idle.png` → Saved to `destination/characters/player/idle.png`

**Combine with resizing**:
- `50% ui§icons§menu.png` → Resized to 50% and saved to `destination/ui/icons/menu.png`

### File Filtering

Ignore specific file types by extension:

```json
{
  "ignore_extensions": [".txt", ".bak", ".bak.png", ".tmp"]
}
```

Supports multi-part extensions (e.g., `.bak.png`)

## Troubleshooting

### "pngquant not found"
- Install pngquant from [pngquant.org](https://pngquant.org/)
- Add pngquant to your system PATH, or specify the full path in `config.json`

### "ImageMagick not found"
- Install ImageMagick from [imagemagick.org](https://imagemagick.org/)
- Make sure to check "Add to PATH" during installation

### Files not being monitored
- Check that source folder paths in `config.json` are correct
- Ensure the folder exists before starting the script
- Verify the file extension isn't in the `ignore_extensions` list

### Compression not working
- Verify pngquant is installed and accessible
- Check the `pngquant_path` in config if specified
- Enable `debug: true` in config to see detailed compression logs


## License

This project is open source and available for personal and commercial use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on the GitHub repository.

## License

This project is provided as-is for personal or commercial use.
