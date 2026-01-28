@echo off
REM Build Work Logger as standalone executable
REM This creates a single .exe file that can be shared

cd /d "%~dp0"
echo Building Work Logger executable...
echo.

python build_exe.py

echo.
pause
