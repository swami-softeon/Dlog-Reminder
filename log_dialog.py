"""
Log Entry Popup Dialog for Work Logger.
Provides a quick-entry form for logging work activities.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QShortcut,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence

from config import DEFAULT_TASK_TYPES, REMINDER_INTERVAL_MINUTES
from data_store import DataStore


class LogEntryDialog(QDialog):
    """
    Popup dialog for entering work log entries.
    
    Signals:
        entry_saved: Emitted when an entry is successfully saved
        snoozed: Emitted when user requests snooze
        skipped: Emitted when user skips the entry
    """
    
    entry_saved = pyqtSignal()
    snoozed = pyqtSignal()
    skipped = pyqtSignal()
    
    def __init__(self, data_store: DataStore, parent=None):
        super().__init__(parent)
        self.data_store = data_store
        self._setup_ui()
        self._setup_shortcuts()
        self._load_previous_values()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Work Logger")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.Dialog |
            Qt.WindowCloseButtonHint
        )
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Question label
        question_label = QLabel(
            f"What did you work on in the last {REMINDER_INTERVAL_MINUTES} minutes?"
        )
        question_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        layout.addWidget(question_label)
        
        # Description field (mandatory, auto-focused)
        desc_label = QLabel("Description: *")
        layout.addWidget(desc_label)
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Enter what you worked on...")
        self.description_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.description_edit)
        
        # Project dropdown (editable, remembers last value)
        project_label = QLabel("Project:")
        layout.addWidget(project_label)
        
        self.project_combo = QComboBox()
        self.project_combo.setEditable(True)
        self.project_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.project_combo)
        
        # Task Type dropdown
        task_label = QLabel("Task Type:")
        layout.addWidget(task_label)
        
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(DEFAULT_TASK_TYPES)
        self.task_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.task_type_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save (Enter)")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)
        
        self.snooze_btn = QPushButton("Snooze 10m (Ctrl+S)")
        self.snooze_btn.clicked.connect(self._on_snooze)
        button_layout.addWidget(self.snooze_btn)
        
        self.skip_btn = QPushButton("Skip (Esc)")
        self.skip_btn.clicked.connect(self._on_skip)
        button_layout.addWidget(self.skip_btn)
        
        layout.addLayout(button_layout)
        
        # Status label for validation errors
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Enter to save (handled by default button)
        
        # Escape to skip
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc_shortcut.activated.connect(self._on_skip)
        
        # Ctrl+S to snooze
        self.snooze_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.snooze_shortcut.activated.connect(self._on_snooze)
    
    def _load_previous_values(self):
        """Load previous project and task type values."""
        # Load projects
        projects = self.data_store.get_all_projects()
        self.project_combo.addItems(projects)
        
        # Set last used project
        last_project = self.data_store.get_last_project()
        if last_project:
            index = self.project_combo.findText(last_project)
            if index >= 0:
                self.project_combo.setCurrentIndex(index)
            else:
                self.project_combo.setEditText(last_project)
        
        # Set last used task type
        last_task_type = self.data_store.get_last_task_type()
        if last_task_type:
            index = self.task_type_combo.findText(last_task_type)
            if index >= 0:
                self.task_type_combo.setCurrentIndex(index)
    
    def _on_save(self):
        """Handle save button click."""
        description = self.description_edit.text().strip()
        
        if not description:
            self.status_label.setText("Description is required!")
            self.description_edit.setFocus()
            return
        
        project = self.project_combo.currentText().strip()
        task_type = self.task_type_combo.currentText()
        
        try:
            self.data_store.save_entry(project, task_type, description)
            self.entry_saved.emit()
            self.accept()
        except Exception as e:
            self.status_label.setText(f"Error saving: {str(e)}")
    
    def _on_snooze(self):
        """Handle snooze button click."""
        self.snoozed.emit()
        self.reject()
    
    def _on_skip(self):
        """Handle skip button click."""
        self.skipped.emit()
        self.reject()
    
    def showEvent(self, event):
        """Focus on description field when dialog is shown."""
        super().showEvent(event)
        self.description_edit.setFocus()
        self.status_label.setText("")
        self.description_edit.clear()
        
        # Reload previous values each time
        self._load_previous_values()
        
        # Center on screen
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
