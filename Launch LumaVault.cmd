@echo off
cd /d "%~dp0"
if exist "dist\LumaVault\LumaVault.exe" (
  start "" "dist\LumaVault\LumaVault.exe"
  exit /b 0
)
if exist ".venv\Scripts\pythonw.exe" (
  start "" ".venv\Scripts\pythonw.exe" "main.py"
  exit /b 0
)
echo LumaVault is not built yet. Run build.bat first.
pause
