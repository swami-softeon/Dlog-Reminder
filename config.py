"""
Configuration constants for Work Logger application.
"""

import os
from pathlib import Path

# Reminder interval in minutes
REMINDER_INTERVAL_MINUTES = 45

# Snooze duration in minutes
SNOOZE_DURATION_MINUTES = 10

# Data storage path (default - can be changed in settings)
WORKLOG_DIR = Path("D:/dailylogs")

# Default task types
DEFAULT_TASK_TYPES = [
    "Development",
    "Meeting",
    "Review",
    "Learning",
    "Support",
    "Other"
]

# Application settings
APP_NAME = "Work Logger"
APP_ICON = None  # Will use default system icon
