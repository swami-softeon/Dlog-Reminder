# Work Logger

A lightweight Windows system-tray application that periodically prompts you to log what you worked on, stores the data locally, and provides a clean daily summary.

## Features

- **System Tray Application**: Runs quietly in your Windows system tray
- **Periodic Reminders**: Popup appears every 45 minutes (configurable)
- **Quick Entry**: Log your work in under 20 seconds with keyboard shortcuts
- **Local Storage**: All data stored locally in CSV files (`~/worklog/`)
- **Daily Summary**: View and copy your daily work summary grouped by project and task type

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

Double-click `run_worklogger.bat` or run:
```bash
python main.py
```

The application will appear in your system tray.

### Tray Menu Options

Right-click the tray icon to access:
- **📝 Log Now** - Manually open the log entry popup
- **📊 Today's Summary** - View grouped summary of today's work
- **⏸️ Pause Reminders** - Temporarily pause automatic reminders
- **❌ Exit** - Close the application

### Log Entry Popup

When the popup appears:

| Field | Description |
|-------|-------------|
| Description | What you worked on (required) |
| Project | Project name (editable dropdown, remembers last used) |
| Task Type | Category of work (Development, Meeting, Review, Learning, Support, Other) |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Save entry |
| Esc | Skip (dismiss without saving) |
| Ctrl+S | Snooze for 10 minutes |

## Data Storage

Work logs are stored in `~/worklog/` as daily CSV files:
- Format: `YYYY-MM-DD.csv`
- Schema: `date,start_time,end_time,project,task_type,description`

## Configuration

Edit `config.py` to customize:
- `REMINDER_INTERVAL_MINUTES` - How often reminders appear (default: 45)
- `SNOOZE_DURATION_MINUTES` - Snooze duration (default: 10)
- `DEFAULT_TASK_TYPES` - Available task type options

## Summary View

The summary groups entries by Project and Task Type, showing:
- Total time spent on each combination
- List of descriptions/tasks completed

Example:
```
WMS – Development – 2h 15m
  • Conveyor PLC integration
  • Robot ACK timeout debugging

WMS – Meeting – 45m
  • Sprint planning
```

Use the "Copy to Clipboard" button to paste into your official daily log.

## Auto-Start (Optional)

To start Work Logger automatically with Windows:
1. Press `Win + R`, type `shell:startup`, press Enter
2. Create a shortcut to `run_worklogger.bat` in the opened folder

## License

MIT License - Use freely for personal or commercial purposes.
