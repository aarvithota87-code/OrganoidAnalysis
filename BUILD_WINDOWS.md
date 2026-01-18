# Building Windows Desktop Application (MSI Installer)

This guide explains how to package the Organoid Analysis Flask application as a Windows desktop application with an MSI installer.

## Prerequisites

### 1. Python Environment (Windows)
```powershell
# Install Python 3.7+ from python.org
python --version

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Install PyInstaller
```powershell
pip install pyinstaller
```

### 3. Install WiX Toolset (for MSI creation)
Download and install WiX Toolset from: https://wixtoolset.org/releases/

Add WiX to your PATH or install to default location: `C:\Program Files (x86)\WiX Toolset v3.11\bin`

## Building Steps

### Step 1: Build with PyInstaller (OneDir Mode)

```powershell
pyinstaller desktop_app.spec --onedir --noconsole
```

This creates:
- `dist/OrganoidAnalysis/` - Complete application folder
- `build/` - Build artifacts (can be deleted)

### Step 2: Test the Application

Before creating installer, test the built application:
```powershell
cd dist\OrganoidAnalysis
.\OrganoidAnalysis.exe
```

The application should:
- Launch without console window
- Automatically open browser to http://127.0.0.1:5174
- Display the web interface

### Step 3: Prepare MSI Installer (WiX Method)

#### Option A: Using WiX (Recommended for MSI)

1. Create a WiX project file `installer.wxs`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" Name="Organoid Analysis" Language="1033" Version="1.0.0.0" Manufacturer="Your Company" UpgradeCode="YOUR-GUID-HERE">
        <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
        
        <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
        <MediaTemplate />
        
        <Feature Id="ProductFeature" Title="Organoid Analysis" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
        </Feature>
    </Product>
    
    <Fragment>
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLFOLDER" Name="OrganoidAnalysis">
                    <Component Id="MainExecutable" Guid="YOUR-GUID-HERE">
                        <File Id="OrganoidAnalysisExe" Source="dist\OrganoidAnalysis\OrganoidAnalysis.exe" KeyPath="yes" />
                    </Component>
                </Directory>
            </Directory>
        </Directory>
    </Fragment>
    
    <Fragment>
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            <Component Id="CopyFiles" Guid="YOUR-GUID-HERE">
                <File Source="dist\OrganoidAnalysis\*" />
                <RemoveFolder Id="RemoveINSTALLFOLDER" On="uninstall" />
            </Component>
        </ComponentGroup>
    </Fragment>
</Wix>
```

2. Build MSI using WiX:
```powershell
candle installer.wxs -out installer.wixobj
light installer.wixobj -out OrganoidAnalysis-Installer.msi
```

#### Option B: Using Inno Setup (Easier, creates EXE installer)

Download Inno Setup from: https://jrsoftware.org/isinfo.php

Create `setup.iss`:
```ini
[Setup]
AppName=Organoid Analysis
AppVersion=1.0
DefaultDirName={pf}\OrganoidAnalysis
DefaultGroupName=Organoid Analysis
OutputDir=dist
OutputBaseFilename=OrganoidAnalysis-Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\OrganoidAnalysis\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Organoid Analysis"; Filename: "{app}\OrganoidAnalysis.exe"
Name: "{commondesktop}\Organoid Analysis"; Filename: "{app}\OrganoidAnalysis.exe"

[Run]
Filename: "{app}\OrganoidAnalysis.exe"; Description: "Launch Organoid Analysis"; Flags: nowait postinstall skipifsilent
```

Compile with Inno Setup Compiler.

### Step 4: Include Prerequisites in Installer

You'll need to check for and install prerequisites:

#### Prerequisites to Check/Install:

1. **Visual C++ Redistributable (x64)**
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Silent install: `vc_redist.x64.exe /install /quiet /norestart`

2. **WebView2 Runtime** (if using embedded browser)
   - Download: https://go.microsoft.com/fwlink/p/?LinkId=2124703
   - Usually pre-installed on Windows 10/11

#### Adding Prerequisites Check to WiX:

```xml
<Property Id="VC_REDIST">
    <RegistrySearch Id="VCRedist" Root="HKLM" Key="SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" Name="Version" Type="raw" />
</Property>

<Condition Message="Visual C++ Redistributable 2015-2022 x64 is required. Please install it first.">
    VC_REDIST
</Condition>
```

Or use a bootstrapper like Burn (WiX) or bundle with Inno Setup.

## Alternative: Simple Batch Launcher

For a simpler distribution without MSI, create a launcher script:

**launch.bat**:
```batch
@echo off
cd /d "%~dp0"
start "" "OrganoidAnalysis.exe"
timeout /t 2
start http://127.0.0.1:5174
```

## File Structure After Build

```
OrganoidAnalysis ExtraMethods/
├── dist/
│   └── OrganoidAnalysis/
│       ├── OrganoidAnalysis.exe
│       ├── _internal/
│       ├── templates/
│       ├── static/
│       └── [other files]
├── build/
└── OrganoidAnalysis-Installer.msi (after MSI build)
```

## Troubleshooting

### Issue: Application won't start
- Check that all DLLs are included
- Verify template and static folders are bundled
- Check PyInstaller logs in `build/OrganoidAnalysis/warn-*.txt`

### Issue: Templates/static files not found
- Verify `datas` in `.spec` file includes all folders
- Check paths in `desktop_app.py` use `sys._MEIPASS`

### Issue: Port already in use
- Change port in `desktop_app.py` (line with `port = 5174`)
- Or kill existing process using port 5174

## Distribution Checklist

- [ ] Test application on clean Windows machine
- [ ] Verify all dependencies are included
- [ ] Include VC++ Redistributable installer or check
- [ ] Create installer (MSI/EXE)
- [ ] Test installation process
- [ ] Create user documentation
- [ ] Package final installer for distribution

## Notes

- The application runs Flask server on `127.0.0.1:5174` locally
- No internet connection required for operation
- All analysis happens locally on the machine
- Generated files are stored in `static/uploads/` folder

