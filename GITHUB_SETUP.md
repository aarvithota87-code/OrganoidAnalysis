# GitHub Actions Setup Guide

This guide will help you set up automated Windows builds using GitHub Actions.

## Step 1: Initialize Git Repository (if not already done)

```bash
cd "/Users/kamalakarthota/Downloads/OrganoidAnalysis ExtraMethods"

# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: Organoid Analysis Web Application with Windows build support"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com and sign in
2. Click the **"+" icon** in top right → **"New repository"**
3. Repository name: `OrganoidAnalysis` (or your preferred name)
4. Description: "Organoid cell growth analysis application with multiple CV methods"
5. **Make it Public** (required for free GitHub Actions)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

## Step 3: Connect Local Repository to GitHub

GitHub will show you commands. Use these:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/OrganoidAnalysis.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Verify Workflow File is Present

The workflow file should be at:
```
.github/workflows/build-windows.yml
```

If it's there, you're ready! If not, make sure you committed it:

```bash
git add .github/workflows/build-windows.yml
git commit -m "Add GitHub Actions workflow for Windows build"
git push
```

## Step 5: Trigger the Build

### Method 1: Manual Trigger (Recommended for first test)

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/OrganoidAnalysis`
2. Click on the **"Actions"** tab
3. You should see "Build Windows Application" workflow on the left
4. Click **"Build Windows Application"**
5. Click **"Run workflow"** button (right side)
6. Select branch: `main`
7. Click green **"Run workflow"** button

### Method 2: Push a Tag (For releases)

```bash
# Create a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

This will automatically trigger the build.

## Step 6: Download the Built Executable

1. Go to **Actions** tab
2. Click on the latest workflow run (e.g., "Build Windows Application #1")
3. Wait for it to complete (green checkmark)
4. Scroll down to **"Artifacts"** section
5. Click **"OrganoidAnalysis-Windows"** to download
6. Extract the ZIP file
7. You'll find `OrganoidAnalysis.exe` in the extracted folder

## What the Workflow Does

The GitHub Actions workflow will:

1. ✅ Checkout your code on Windows Server
2. ✅ Install Python 3.9
3. ✅ Install all dependencies from `requirements.txt`
4. ✅ Install PyInstaller
5. ✅ Build Windows executable using `desktop_app.spec`
6. ✅ Create ZIP archive
7. ✅ Upload as downloadable artifact
8. ✅ (Optional) Create GitHub Release if you push a tag

## Build Time

- First build: ~5-10 minutes (installing dependencies)
- Subsequent builds: ~3-5 minutes

## Troubleshooting

### Workflow doesn't appear
- Make sure `.github/workflows/build-windows.yml` is committed and pushed
- Check the file path is correct: `.github/workflows/` (with dot at start)

### Build fails
- Check the Actions log for error messages
- Common issues:
  - Missing files in repository
  - Import errors in Python code
  - Missing dependencies in `requirements.txt`

### Can't find artifacts
- Wait for the workflow to complete (look for green checkmark)
- Artifacts are only available after successful build
- Artifacts expire after 90 days on free accounts

## Next Steps After Downloading

1. Test the executable on a Windows machine
2. The executable should:
   - Launch without console window
   - Open browser automatically to http://127.0.0.1:5174
   - Display the web interface

## Creating Releases

To create a GitHub Release with the built executable:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

The workflow will automatically:
- Build the executable
- Create a GitHub Release
- Attach the ZIP file to the release

## Quick Reference Commands

```bash
# Initialize git (if needed)
git init
git add .
git commit -m "Initial commit"

# Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/OrganoidAnalysis.git
git branch -M main
git push -u origin main

# Push updates
git add .
git commit -m "Update description"
git push

# Create release tag
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

## Need Help?

- GitHub Actions Docs: https://docs.github.com/en/actions
- Check workflow logs in Actions tab for detailed error messages
- Verify all Python files are committed (no `.gitignore` excluding them)

