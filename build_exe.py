"""
Build script to create a standalone executable for Work Logger.
Run this script to generate a portable .exe file.

Requirements:
    pip install pyinstaller

Usage:
    python build_exe.py
"""

import subprocess
import sys
import os

def main():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=WorkLogger",
        "--onefile",           # Single executable file
        "--windowed",          # No console window
        "--noconfirm",         # Overwrite without asking
        "--clean",             # Clean cache before building
        # Add icon if it exists
        # "--icon=icon.ico",
        main_script
    ]
    
    print("Building Work Logger executable...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    if result.returncode == 0:
        exe_path = os.path.join(script_dir, "dist", "WorkLogger.exe")
        print("-" * 50)
        print("✅ Build successful!")
        print(f"\nExecutable created at:\n  {exe_path}")
        print("\nYou can now share this single file with your colleagues.")
        print("No Python installation required on their computers!")
    else:
        print("❌ Build failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
