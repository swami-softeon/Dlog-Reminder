@echo off
REM Work Logger - Startup Script
REM Run this to start the Work Logger application

cd /d "%~dp0"
pythonw main.py

REM If pythonw is not available, use python
if errorlevel 1 (
    python main.py
)
