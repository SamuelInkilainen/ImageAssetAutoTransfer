# Building a Standalone Executable

This guide will help you create a standalone application that your teammates can use without installing Python.

## Prerequisites

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Organize your pngquant folder:
   - Create a folder: `pngquant`
   - Place `pngquant.exe` inside it
   - Your structure should be:
     ```
     ImageAssetAutoTransfer/
     ├── monitor_folder.py
     ├── config.json
     ├── build_executable.py
     └── pngquant/
         └── pngquant.exe
     ```

3. (Optional) If you have OptiPNG, create an `optipng` folder and place `optipng.exe` inside

## Build the Executable

Run the build script:
```bash
python build_executable.py
```

This will create a `dist/FolderMonitor` folder containing:
- `FolderMonitor.exe` - The main executable
- `config.json` - Editable configuration file (template)
- `pngquant/` - Bundled pngquant executable
- `_internal/` - Python runtime and dependencies (don't modify)

## Distribute to Your Team

1. **Zip the entire folder**: Compress `dist/FolderMonitor` into a zip file

2. **Share with teammates**: Send them the zip file

3. **Setup instructions for teammates**:
   - Extract the zip file anywhere on their computer
   - Edit `config.json` with their source/destination folders
   - Double-click `FolderMonitor.exe` to start monitoring
   - Press Ctrl+C in the console to stop

## Important Notes

### Config File
- `config.json` remains **fully editable** - each user can customize paths
- Users can enable/disable compression
- Users can adjust quality settings by editing the file

### Updating pngquant Paths
Since pngquant is bundled, users should use these settings in `config.json`:
```json
{
  "compress_png": true,
  "pngquant_path": "pngquant/pngquant.exe"
}
```

Or simply:
```json
{
  "compress_png": true
}
```
The application will automatically find the bundled pngquant.

### File Size
The executable folder will be around 20-30 MB due to bundled Python runtime.

### Antivirus
Some antivirus software may flag PyInstaller executables. This is a false positive. You can:
- Add an exclusion for the executable
- Have your IT department whitelist it
- Build and sign the executable with a code signing certificate (advanced)

## Advanced: Adding an Icon

To add a custom icon to the executable:

1. Get a `.ico` file for your application
2. Edit `build_executable.py` and change:
   ```python
   "--icon=NONE",
   ```
   to:
   ```python
   "--icon=path/to/your/icon.ico",
   ```

## Troubleshooting

### "pngquant not found" after building
- Make sure `pngquant.exe` is in the `pngquant/` folder before building
- Rebuild using `python build_executable.py`

### Config changes not taking effect
- Make sure you're editing the config.json in the same folder as the .exe
- Restart the application after changing config

### Application won't start
- Try running from command prompt to see error messages
- Check that all files in `_internal/` folder are present
- Verify config.json is valid JSON

## Updating the Application

When you make changes to `monitor_folder.py`:
1. Run `python build_executable.py` again
2. Redistribute the updated `dist/FolderMonitor` folder
