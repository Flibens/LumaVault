@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" uv venv .venv --python 3.11
set PYTHONPATH=
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --onedir --name LumaVault --icon "assets\lumavault.ico" --add-data "lumavault\static;lumavault\static" --hidden-import webview.platforms.edgechromium --collect-all webview main.py
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)
echo.
echo Built: %CD%\dist\LumaVault\LumaVault.exe
pause
