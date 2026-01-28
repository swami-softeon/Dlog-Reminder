"""
System Tray Application for Work Logger.
Main application class that manages the tray icon, menu, and timers.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon

from config import APP_NAME
from data_store import DataStore
from log_dialog import LogEntryDialog
from summary_dialog import SummaryDialog
from settings_dialog import SettingsDialog, load_settings


class WorkLoggerTray(QSystemTrayIcon):
    """
    System tray application for Work Logger.
    Manages periodic reminders and user interactions.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load settings
        self.settings = load_settings()
        
        self.data_store = DataStore()
        self.log_dialog = None
        self.summary_dialog = None
        self.settings_dialog = None
        self.is_paused = False
        
        self._setup_icon()
        self._setup_menu()
        self._setup_timer()
        
        # Show startup notification
        interval = self.settings.get('reminder_interval_minutes', 45)
        self.showMessage(
            APP_NAME,
            f"Work Logger is running. Reminders every {interval} minutes.",
            QSystemTrayIcon.Information,
            3000
        )
    
    def _setup_icon(self):
        """Set up the tray icon."""
        # Use a built-in icon or create a simple one
        # For a production app, you'd want a proper .ico file
        self.setIcon(self._create_default_icon())
        self.setToolTip(APP_NAME)
        self.activated.connect(self._on_tray_activated)
    
    def _create_default_icon(self) -> QIcon:
        """Create a default icon using Qt's built-in resources."""
        # Try to use a system icon, fallback to application icon
        icon = QIcon.fromTheme("appointment-new")
        if icon.isNull():
            icon = QApplication.style().standardIcon(
                QApplication.style().SP_FileDialogDetailedView
            )
        return icon
    
    def _setup_menu(self):
        """Set up the tray context menu."""
        menu = QMenu()
        
        # Log now action
        self.log_now_action = QAction("📝 Log Now", self)
        self.log_now_action.triggered.connect(self.show_log_dialog)
        menu.addAction(self.log_now_action)
        
        # Today's summary action
        self.summary_action = QAction("📊 Today's Summary", self)
        self.summary_action.triggered.connect(self.show_summary_dialog)
        menu.addAction(self.summary_action)
        
        menu.addSeparator()
        
        # Settings action
        self.settings_action = QAction("⚙️ Settings", self)
        self.settings_action.triggered.connect(self.show_settings_dialog)
        menu.addAction(self.settings_action)
        
        # Pause reminders action
        self.pause_action = QAction("⏸️ Pause Reminders", self)
        self.pause_action.setCheckable(True)
        self.pause_action.triggered.connect(self._toggle_pause)
        menu.addAction(self.pause_action)
        
        menu.addSeparator()
        
        # Exit action
        self.exit_action = QAction("❌ Exit", self)
        self.exit_action.triggered.connect(self._exit_app)
        menu.addAction(self.exit_action)
        
        self.setContextMenu(menu)
    
    def _setup_timer(self):
        """Set up the reminder timer."""
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self._on_reminder)
        
        # Convert minutes to milliseconds
        interval = self.settings.get('reminder_interval_minutes', 45)
        interval_ms = interval * 60 * 1000
        self.reminder_timer.start(interval_ms)
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation (double-click, etc.)."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_log_dialog()
    
    def _on_reminder(self):
        """Handle reminder timer timeout."""
        if not self.is_paused:
            self.show_log_dialog()
    
    def show_log_dialog(self):
        """Show the log entry dialog."""
        if self.log_dialog is None or not self.log_dialog.isVisible():
            self.log_dialog = LogEntryDialog(self.data_store)
            self.log_dialog.entry_saved.connect(self._on_entry_saved)
            self.log_dialog.snoozed.connect(self._on_snooze)
            self.log_dialog.skipped.connect(self._on_skipped)
            self.log_dialog.show()
            self.log_dialog.activateWindow()
            self.log_dialog.raise_()
    
    def show_summary_dialog(self):
        """Show today's summary dialog."""
        if self.summary_dialog is None or not self.summary_dialog.isVisible():
            self.summary_dialog = SummaryDialog(self.data_store)
            self.summary_dialog.show()
            self.summary_dialog.activateWindow()
            self.summary_dialog.raise_()
    
    def _on_entry_saved(self):
        """Handle successful entry save."""
        self.showMessage(
            APP_NAME,
            "Entry logged successfully!",
            QSystemTrayIcon.Information,
            2000
        )
        # Reset timer after logging
        self._reset_timer()
    
    def _on_snooze(self):
        """Handle snooze request."""
        snooze_duration = self.settings.get('snooze_duration_minutes', 10)
        self.showMessage(
            APP_NAME,
            f"Snoozed for {snooze_duration} minutes.",
            QSystemTrayIcon.Information,
            2000
        )
        # Set a shorter timer for snooze
        snooze_ms = snooze_duration * 60 * 1000
        self.reminder_timer.start(snooze_ms)
    
    def _on_skipped(self):
        """Handle skip request."""
        # Just reset the timer to normal interval
        self._reset_timer()
    
    def _reset_timer(self):
        """Reset the timer to the normal interval."""
        interval = self.settings.get('reminder_interval_minutes', 45)
        interval_ms = interval * 60 * 1000
        self.reminder_timer.start(interval_ms)
    
    def show_settings_dialog(self):
        """Show the settings dialog."""
        if self.settings_dialog is None or not self.settings_dialog.isVisible():
            self.settings_dialog = SettingsDialog()
            self.settings_dialog.settings_changed.connect(self._on_settings_changed)
            self.settings_dialog.show()
            self.settings_dialog.activateWindow()
            self.settings_dialog.raise_()
    
    def _on_settings_changed(self, new_settings):
        """Handle settings changes."""
        self.settings = new_settings
        # Reset timer with new interval
        self._reset_timer()
    
    def _toggle_pause(self, checked):
        """Toggle pause state for reminders."""
        self.is_paused = checked
        if checked:
            self.pause_action.setText("▶️ Resume Reminders")
            self.showMessage(
                APP_NAME,
                "Reminders paused. Right-click to resume.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.pause_action.setText("⏸️ Pause Reminders")
            self.showMessage(
                APP_NAME,
                "Reminders resumed.",
                QSystemTrayIcon.Information,
                2000
            )
    
    def _exit_app(self):
        """Exit the application."""
        reply = QMessageBox.question(
            None,
            APP_NAME,
            "Are you sure you want to exit Work Logger?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.reminder_timer.stop()
            QApplication.quit()


def main():
    """Main entry point for the application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when dialogs close
    app.setApplicationName(APP_NAME)
    
    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            APP_NAME,
            "System tray is not available on this system."
        )
        return 1
    
    # Create and show tray icon
    tray = WorkLoggerTray()
    tray.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
