# Distribution Guide for Windows Application

## What Gets Built

The GitHub Actions workflow builds **two versions** of your Windows application:

### 1. **OneFile Version** (`OrganoidAnalysis.exe`)
- **Single executable file** (~100-200MB)
- Easy to distribute - just one file
- Slower startup (extracts to temp folder on each run)
- Best for: Simple distribution, USB drives, email

**Usage:** Double-click `OrganoidAnalysis.exe` to run

### 2. **OneDir Version** (`OrganoidAnalysis-Windows-Folder.zip`)
- **Folder with executable + dependencies**
- Faster startup
- Multiple files in a folder
- Best for: Installation to Program Files, better performance

**Usage:** Extract ZIP, run `OrganoidAnalysis/OrganoidAnalysis.exe`

## How It Works

Both versions:
1. ✅ **Bundle everything** - No Python installation needed
2. ✅ **Run on any Windows machine** - Works on Windows 10/11
3. ✅ **Start local server** - Opens browser to http://127.0.0.1:5174
4. ✅ **No internet required** - All processing is local

## Download After Build

After the GitHub Actions build completes:

1. Go to **Actions** tab → Latest workflow run
2. Scroll down to **Artifacts**
3. Download **OrganoidAnalysis-Windows**
4. Extract to see:
   - `OrganoidAnalysis.exe` (single file version)
   - `OrganoidAnalysis-Windows-Folder.zip` (folder version)

## Distribution Options

### Option 1: Single EXE (Recommended for most users)
- Share `OrganoidAnalysis.exe`
- Users just double-click to run
- No installation needed

### Option 2: Folder Version
- Share `OrganoidAnalysis-Windows-Folder.zip`
- Users extract and run `OrganoidAnalysis.exe` inside folder
- Better performance, multiple files

### Option 3: MSI Installer (Advanced)
- Requires WiX Toolset or Inno Setup
- See `BUILD_WINDOWS.md` for MSI creation steps
- Professional installation experience

## User Instructions

**For End Users:**

1. Download `OrganoidAnalysis.exe` (or extract the ZIP folder)
2. Double-click `OrganoidAnalysis.exe`
3. Browser will open automatically to http://127.0.0.1:5174
4. Use the web interface to analyze organoid images
5. No Python, Flask, or dependencies needed!

**Note:** The first run may take 10-20 seconds to start (extracting files).

## Technical Details

- **Built with:** PyInstaller 6.18.0
- **Python:** 3.9.13
- **Platform:** Windows 10/11 (64-bit)
- **Port:** 127.0.0.1:5174 (local only, no network access needed)
- **File size:** ~100-200MB (includes all dependencies)

## Requirements for End Users

✅ **Windows 10 or 11** (64-bit)
✅ **No Python needed** - Everything is bundled
✅ **No installation needed** - Just run the EXE
⚠️ **Firewall may prompt** - Allow if asked (for localhost only)

