# Building Windows Application from macOS

You're on macOS, but need to build a Windows executable. Here are your options:

## Option 1: Use GitHub Actions (Recommended - Free & Easy)

GitHub Actions can build Windows executables automatically when you push to GitHub.

### Setup:

1. Create `.github/workflows/build-windows.yml`:

```yaml
name: Build Windows Application

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build with PyInstaller
      run: |
        pyinstaller desktop_app.spec --onedir --noconsole
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: OrganoidAnalysis-Windows
        path: dist/OrganoidAnalysis/
    
    - name: Create ZIP
      run: |
        Compress-Archive -Path dist\OrganoidAnalysis\* -DestinationPath OrganoidAnalysis-Windows.zip
    
    - name: Upload ZIP
      uses: actions/upload-artifact@v3
      with:
        name: OrganoidAnalysis-Windows-ZIP
        path: OrganoidAnalysis-Windows.zip
```

2. Push to GitHub and trigger the workflow
3. Download the built executable from GitHub Actions artifacts

## Option 2: Windows Virtual Machine

### Using Parallels Desktop (Paid):
- Install Parallels Desktop for Mac
- Install Windows 11 VM
- Build inside the VM

### Using UTM (Free):
- Download UTM from Mac App Store or https://mac.getutm.app
- Create Windows 11 VM (requires Windows license)
- Build inside the VM

### Using VirtualBox (Free):
- Install VirtualBox
- Download Windows 11 ISO
- Create VM and build

## Option 3: Boot Camp (If you have Intel Mac)

- Install Windows via Boot Camp
- Dual boot into Windows
- Build natively

## Option 4: Cloud Windows Instance

### AWS EC2 / Azure / Google Cloud:
- Launch Windows Server instance
- RDP into it
- Build there
- Download the result

### GitHub Codespaces (if available):
- Some plans support Windows containers
- Check GitHub Codespaces documentation

## Option 5: Cross-Compilation (Advanced - Not Recommended)

PyInstaller doesn't officially support cross-compilation. However, you can try:

### Using Wine (Complex):
```bash
# Install Wine
brew install wine-stable

# Install Python for Windows in Wine
wine msiexec /i python-3.9.x.msi

# Install PyInstaller in Wine Python
wine python.exe -m pip install pyinstaller

# Build (may have issues)
wine python.exe -m PyInstaller desktop_app.spec
```

**Note:** This is unreliable and may not work properly due to DLL dependencies.

## Option 6: Prepare on Mac, Build on Windows Later

You can prepare everything on Mac and build when you have access to Windows:

### What you can do on Mac:

1. **Test the desktop_app.py works:**
```bash
python3 desktop_app.py
# Should open browser to http://127.0.0.1:5174
```

2. **Verify all files are included in .spec:**
```bash
# Check that desktop_app.spec lists all needed files
cat desktop_app.spec
```

3. **Create a build checklist:**
   - All Python files present
   - templates/ folder exists
   - static/ folder structure exists
   - methods_explanation.html exists

4. **Test imports work:**
```bash
python3 -c "from desktop_app import app; print('All imports OK')"
```

## Recommended Approach: GitHub Actions

**Why GitHub Actions is best:**
- ✅ Free for public repos
- ✅ No Windows license needed
- ✅ Automated builds
- ✅ Easy to share/distribute
- ✅ Can build on every release

### Quick Setup:

1. Create GitHub repo (if not already)
2. Add the workflow file (see Option 1)
3. Push your code
4. Go to Actions tab
5. Run workflow manually or push a tag
6. Download the built executable

## Testing Before Building

On your Mac, you can verify everything works:

```bash
# Test the desktop app wrapper
python3 desktop_app.py

# Should:
# 1. Start Flask server
# 2. Open browser automatically
# 3. Show the web interface
```

If this works on Mac, it will work on Windows (just needs PyInstaller build).

## Summary

**Easiest:** Use GitHub Actions (free, automated)
**Most Control:** Windows VM on your Mac
**Quick Test:** Prepare on Mac, build later on any Windows machine

The code is ready - you just need a Windows environment to run PyInstaller!

