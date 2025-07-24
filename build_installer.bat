@echo off
echo Installing required packages...
pip install pygame Pillow mutagen pyinstaller

echo Building executable with PyInstaller...
pyinstaller --noconfirm --onefile --windowed --name=VibeJoy --icon=NONE main.py

echo Build complete! Check the 'dist' folder for VibeJoy.exe
pause