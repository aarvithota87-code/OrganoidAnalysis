@echo off
echo Building Organoid Analysis Windows Application...
echo.

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building with PyInstaller...
pyinstaller desktop_app.spec --onedir --noconsole

echo.
echo Build complete! Check dist\OrganoidAnalysis folder
echo.
echo To test, run: dist\OrganoidAnalysis\OrganoidAnalysis.exe
echo.
pause

