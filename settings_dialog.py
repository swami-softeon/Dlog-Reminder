"""
Settings Dialog for Work Logger.
Allows users to configure reminder intervals and other options.
"""

import json
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QGroupBox, QFormLayout,
    QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from config import WORKLOG_DIR, REMINDER_INTERVAL_MINUTES, SNOOZE_DURATION_MINUTES


def get_settings_file() -> Path:
    """Get the settings file path (stored in worklog directory)."""
    # First try to read existing settings to find worklog_dir
    # Check default location first
    default_settings_file = WORKLOG_DIR / "settings.json"
    if default_settings_file.exists():
        try:
            with open(default_settings_file, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                worklog_dir = saved.get('worklog_dir', str(WORKLOG_DIR))
                return Path(worklog_dir) / "settings.json"
        except:
            pass
    return default_settings_file


def load_settings() -> dict:
    """Load settings from file, or return defaults."""
    defaults = {
        "reminder_interval_minutes": REMINDER_INTERVAL_MINUTES,
        "snooze_duration_minutes": SNOOZE_DURATION_MINUTES,
        "worklog_dir": str(WORKLOG_DIR)
    }
    
    settings_file = get_settings_file()
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                defaults.update(saved)
        except:
            pass
    
    return defaults


def save_settings(settings: dict) -> None:
    """Save settings to file in the worklog directory."""
    worklog_dir = Path(settings.get('worklog_dir', str(WORKLOG_DIR)))
    worklog_dir.mkdir(parents=True, exist_ok=True)
    settings_file = worklog_dir / "settings.json"
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


class SettingsDialog(QDialog):
    """
    Dialog for configuring Work Logger settings.
    
    Signals:
        settings_changed: Emitted when settings are saved
    """
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = load_settings()
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Settings")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Timer Settings Group
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QFormLayout()
        
        # Reminder interval
        self.reminder_spin = QSpinBox()
        self.reminder_spin.setRange(5, 240)
        self.reminder_spin.setSuffix(" minutes")
        self.reminder_spin.setToolTip("How often the reminder popup appears")
        timer_layout.addRow("Reminder Interval:", self.reminder_spin)
        
        # Snooze duration
        self.snooze_spin = QSpinBox()
        self.snooze_spin.setRange(1, 60)
        self.snooze_spin.setSuffix(" minutes")
        self.snooze_spin.setToolTip("How long to snooze when you press Ctrl+S")
        timer_layout.addRow("Snooze Duration:", self.snooze_spin)
        
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)
        
        # Storage Settings Group
        storage_group = QGroupBox("Storage Settings")
        storage_layout = QFormLayout()
        
        # Worklog directory
        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit()
        self.dir_edit.setToolTip("Folder where daily log files will be stored")
        dir_layout.addWidget(self.dir_edit)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(self.browse_btn)
        
        storage_layout.addRow("Log Directory:", dir_layout)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # Open folder button
        self.open_folder_btn = QPushButton("📂 Open Log Folder")
        self.open_folder_btn.clicked.connect(self._open_log_folder)
        layout.addWidget(self.open_folder_btn)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Status label for validation messages
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
    
    def _load_current_settings(self):
        """Load current settings into the UI."""
        self.reminder_spin.setValue(self.settings.get("reminder_interval_minutes", 45))
        self.snooze_spin.setValue(self.settings.get("snooze_duration_minutes", 10))
        self.dir_edit.setText(self.settings.get("worklog_dir", str(WORKLOG_DIR)))
    
    def _browse_directory(self):
        """Open directory browser."""
        current_dir = self.dir_edit.text()
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Log Directory",
            current_dir
        )
        if new_dir:
            self.dir_edit.setText(new_dir)
    
    def _open_log_folder(self):
        """Open the log folder in Windows Explorer."""
        import subprocess
        folder = self.dir_edit.text()
        if os.path.exists(folder):
            subprocess.Popen(f'explorer "{folder}"')
        else:
            QMessageBox.warning(
                self,
                "Folder Not Found",
                f"The folder does not exist yet:\n{folder}\n\nIt will be created when you log your first entry."
            )
    
    def _on_save(self):
        """Save settings and close dialog."""
        worklog_dir = self.dir_edit.text().strip()
        
        # Validate directory path
        if not worklog_dir:
            self.status_label.setText("Log directory cannot be empty!")
            return
        
        # Normalize path
        worklog_dir = os.path.normpath(worklog_dir)
        
        # Try to create directory if it doesn't exist
        try:
            worklog_path = Path(worklog_dir)
            if not worklog_path.exists():
                reply = QMessageBox.question(
                    self,
                    "Create Directory",
                    f"The directory does not exist:\n{worklog_dir}\n\nDo you want to create it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    worklog_path.mkdir(parents=True, exist_ok=True)
                else:
                    return
            
            # Verify we can write to the directory
            test_file = worklog_path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except PermissionError:
                self.status_label.setText(f"Cannot write to directory: {worklog_dir}")
                return
            except Exception as e:
                self.status_label.setText(f"Error accessing directory: {str(e)}")
                return
                
        except Exception as e:
            self.status_label.setText(f"Invalid directory path: {str(e)}")
            return
        
        self.settings = {
            "reminder_interval_minutes": self.reminder_spin.value(),
            "snooze_duration_minutes": self.snooze_spin.value(),
            "worklog_dir": worklog_dir
        }
        
        save_settings(self.settings)
        self.settings_changed.emit(self.settings)
        
        QMessageBox.information(
            self,
            "Settings Saved",
            f"Settings have been saved.\n\nLog files will be stored in:\n{worklog_dir}\n\nNote: Timer changes will take effect after the next reminder."
        )
        
        self.accept()
    
    def showEvent(self, event):
        """Reload settings when dialog is shown."""
        super().showEvent(event)
        self.settings = load_settings()
        self._load_current_settings()
        self.status_label.setText("")
        
        # Center on screen
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
