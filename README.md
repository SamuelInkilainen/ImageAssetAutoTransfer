Disclaimer: This project is built entirely with Claude Sonnet 4.5 AI model and Github Copilot 

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
- **Skip Compression Prefix**: Selectively disable compression for specific files using a filename prefix
- **Image Resizing**: Parse resize percentage from filename (e.g., `50% image.png` resizes to 50%)
- **Automatic Scale Cleanup**: Automatically deletes old scale variations when saving new ones (e.g., saving `50% file.png` deletes `75% file.png`)
- **Filename Path Parsing**: Extract subfolder paths from filenames using a delimiter (e.g., `folder§subfolder§file.png`)
- **Path Macros**: Define shorthand macros that reroute files to different destination paths (e.g., `ui§button.png` → a completely different folder)
- **File Stabilization**: Smart waiting that ensures complete files are transferred, even with complex save operations
- **Runtime Debug Toggle**: Toggle debug output on/off while running without restarting the script
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
  "ignore_files_without_extension": true,
  "processing_delay": 0.25,
  "compress_png": true,
  "parse_filename_paths": true,
  "filename_path_delimiter": "§",
  "parse_resize_from_filename": true,
  "skip_compression_prefix_enabled": false,
  "skip_compression_prefix": "!",
  "path_macros": {
    "ui": "C:\\Users\\You\\GameProject\\UI\\cocosstudio"
  },
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
| `ignore_files_without_extension` | boolean | No | Ignore files without file extensions (e.g., temp files) (default: false) |
| `processing_delay` | number | No | Poll interval in seconds for file stabilization (waits until file stops changing) (default: 0) |
| `compress_png` | boolean | No | Enable high-quality PNG compression (default: false) |
| `parse_filename_paths` | boolean | No | Extract folder paths from filenames (default: false) |
| `filename_path_delimiter` | string | No | Delimiter for filename paths (default: "§") |
| `parse_resize_from_filename` | boolean | No | Parse resize percentage from filename (default: false) |
| `skip_compression_prefix_enabled` | boolean | No | Enable skip compression prefix feature (default: false) |
| `skip_compression_prefix` | string | No | Prefix that disables compression for files (default: "!") |
| `path_macros` | object | No | Dictionary of shorthand macros that reroute files to different absolute paths (default: {}) |
| `pngquant_path` | string | No | Path to pngquant executable (auto-detected if bundled) |
| `optipng_path` | string | No | Path to optipng executable (auto-detected if bundled) |
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

### Runtime Commands

While the script is running, you can type commands in the console:

- `debug true` - Enable debug output to see detailed processing information
- `debug false` - Disable debug output for cleaner logs

This allows you to troubleshoot issues without restarting the monitoring process.

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

### Skip Compression Prefix

Selectively disable PNG compression for specific files by adding a prefix to the filename. This is useful when you have pre-optimized images or assets that shouldn't be recompressed.

**Configuration:**
```json
{
  "skip_compression_prefix_enabled": true,
  "skip_compression_prefix": "!"
}
```

**Examples**:
- `!logo.png` → Copied as `logo.png` (no compression, prefix removed)
- `!character_sprite.png` → Copied as `character_sprite.png` (no compression)
- `background.png` → Copied as `background.png` (compressed normally if `compress_png` is true)

**Custom Prefixes:**

You can use any single character or string as the prefix:

```json
{
  "skip_compression_prefix": "RAW_"
}
```

- `RAW_texture.png` → Copied as `texture.png` (no compression)

**Combining with Other Features:**
- `!50% icon.png` → Resized to 50%, no compression, saved as `icon.png`
- `!ui§buttons§save.png` → No compression, saved to `ui/buttons/save.png`

**Processing Order**: Copy → Resize (if applicable) → Compress (skipped if prefix detected)

**Notes:**
- The prefix is automatically removed from the destination filename
- Only affects PNG files (compression is PNG-only)
- Files without the prefix are processed normally

### Image Resizing

Automatically resize images by adding a percentage prefix to the filename:

**Examples**:
- `50% character.png` → Resizes to 50% of original dimensions
- `25% background.jpg` → Resizes to 25% of original dimensions

**Requirements**: Install [ImageMagick](https://imagemagick.org/)

**Processing Order**: Copy → Resize → Compress (if PNG)

**Automatic Scale Variation Cleanup**:

When you save a file with a scale prefix, the script automatically deletes other scale variations from the source folder to prevent conflicts:

- Save `50% badge.png` → Automatically deletes `75% badge.png`, `90% badge.png`, etc.
- Save `25% icon.png` → Automatically deletes any other `XX% icon.png` files
- Only files with the same base name are affected (different files are unaffected)

This ensures you always have only one scale variation per asset in your source folder and prevents accidentally transferring outdated versions.

### Filename Path Parsing

Encode subfolder structure directly in filenames using a delimiter:

**Example with delimiter `§`**:
- `ui§buttons§save.png` → Saved to `destination/ui/buttons/save.png`
- `characters§player§idle.png` → Saved to `destination/characters/player/idle.png`

**Combine with resizing**:
- `50% ui§icons§menu.png` → Resized to 50% and saved to `destination/ui/icons/menu.png`

### Path Macros

Define shorthand macros that reroute files to entirely different destination paths. This is useful when your project has multiple output directories but you want to keep filenames short.

When `parse_filename_paths` is enabled, the first segment before the delimiter is checked against `path_macros`. If it matches, the file is routed to that macro's absolute path instead of the normal `destination_folder`.

**Configuration:**
```json
{
  "destination_folder": "C:\\Project\\Resources\\textures",
  "path_macros": {
    "ui": "C:\\Project\\Resources\\ui\\cocosstudio",
    "audio": "C:\\Project\\Resources\\sounds"
  }
}
```

**Examples:**
- `ui§buttons§save.png` → `C:\Project\Resources\ui\cocosstudio\buttons\save.png`
- `ui§icon.png` → `C:\Project\Resources\ui\cocosstudio\icon.png`
- `audio§click.wav` → `C:\Project\Resources\sounds\click.wav`
- `icons§menu.png` (no macro match) → `C:\Project\Resources\textures\icons\menu.png`

**Combine with resizing and compression:**
- `25% ui§badges§badge_neon.png` → Resized to 25%, compressed, saved to `ui\cocosstudio\badges\badge_neon.png`

**Notes:**
- Macros only match the first path segment (before the first `§`)
- Matching is case-sensitive (`ui` ≠ `UI`)
- Requires `parse_filename_paths` to be enabled
- Files without a matching macro use the normal `destination_folder`

### File Filtering

Ignore specific file types by extension:

```json
{
  "ignore_extensions": [".txt", ".bak", ".bak.png", ".tmp"]
}
```

Supports multi-part extensions (e.g., `.bak.png`)

### Handling Photoshop Temporary Files

Photoshop and other editing software often create temporary files (e.g., `filename_tmp2035`) during save operations. Two strategies help prevent these from being processed:

**1. Ignore Files Without Extensions**

Temporary files typically have no file extension. Enable this to skip them:

```json
{
  "ignore_files_without_extension": true
}
```

**2. Processing Delay with File Stabilization**

Wait for files to stabilize before processing, allowing the software to complete its save operations:

```json
{
  "processing_delay": 0.25
}
```

- The script polls the file every `processing_delay` seconds
- Processing begins only when the file's size and modification time stop changing
- Automatically handles complex save operations (modify → delete → recreate → write)
- Maximum wait time: ~10 seconds (then processes anyway)
- Recommended value: `0.25` seconds for responsive monitoring

**How it works:**
1. File change detected → Start monitoring
2. Check file size and modification time every 0.25s
3. When two consecutive checks match → File is stable, begin processing
4. If file disappears during monitoring → Skip (was a temp file)

**Recommended Configuration for Photoshop/Design Tools:**

```json
{
  "ignore_files_without_extension": true,
  "processing_delay": 0.25
}
```

This combination ensures temporary files are filtered out and the file stabilization system waits for the complete file to be saved before processing.

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

### Temporary files being processed
- Enable `ignore_files_without_extension: true` to skip files without extensions
- Add a `processing_delay` (e.g., `1.0` seconds) to allow software to clean up temp files
- See "Handling Photoshop Temporary Files" section for details

### Compression not working
- Verify pngquant is installed and accessible
- Check the `pngquant_path` in config if specified
- Enable `debug: true` in config to see detailed compression logs
- Or type `debug true` in the console while running for real-time debug output

### Old file content being transferred
- The file stabilization system should handle this automatically
- Try increasing `processing_delay` to `0.5` if issues persist
- Enable debug mode (`debug true`) to see stabilization timing
- Check that no other process is modifying files during transfer


## License

This project is provided as-is for personal or commercial use.
