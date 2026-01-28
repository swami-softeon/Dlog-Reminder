"""
Summary View Dialog for Work Logger.
Displays a grouped summary of today's work entries.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QApplication
)
from PyQt5.QtCore import Qt
from datetime import date

from data_store import DataStore


class SummaryDialog(QDialog):
    """
    Dialog showing today's work summary grouped by Project and Task Type.
    Includes copy-to-clipboard functionality.
    """
    
    def __init__(self, data_store: DataStore, parent=None):
        super().__init__(parent)
        self.data_store = data_store
        self._setup_ui()
        self._load_summary()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Today's Summary")
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowCloseButtonHint
        )
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(f"Work Summary for {date.today().strftime('%A, %B %d, %Y')}")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Summary text area
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11pt;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.summary_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_summary)
        button_layout.addWidget(self.refresh_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: green;")
        layout.addWidget(self.status_label)
    
    def _load_summary(self):
        """Load and display today's summary."""
        summary_text = self.data_store.format_summary()
        self.summary_text.setPlainText(summary_text)
        self.status_label.setText("")
    
    def _copy_to_clipboard(self):
        """Copy summary to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.summary_text.toPlainText())
        self.status_label.setText("Copied to clipboard!")
    
    def showEvent(self, event):
        """Refresh summary when dialog is shown."""
        super().showEvent(event)
        self._load_summary()
        
        # Center on screen
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
