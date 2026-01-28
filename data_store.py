"""
CSV data storage module for Work Logger.
Handles reading and writing work log entries to daily CSV files.
"""

import csv
import os
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from config import WORKLOG_DIR


def get_worklog_dir() -> Path:
    """Get the worklog directory from settings, or use default."""
    # Import here to avoid circular import
    try:
        from settings_dialog import load_settings
        settings = load_settings()
        return Path(settings.get('worklog_dir', str(WORKLOG_DIR)))
    except:
        return WORKLOG_DIR


def ensure_worklog_dir() -> Path:
    """Create worklog directory if it doesn't exist and return it."""
    worklog_dir = get_worklog_dir()
    worklog_dir.mkdir(parents=True, exist_ok=True)
    return worklog_dir


@dataclass
class LogEntry:
    """Represents a single work log entry."""
    date: str
    start_time: str
    end_time: str
    project: str
    task_type: str
    description: str


class DataStore:
    """Handles CSV-based storage for work log entries."""
    
    CSV_HEADERS = ['date', 'start_time', 'end_time', 'project', 'task_type', 'description']
    
    def __init__(self):
        self.worklog_dir = ensure_worklog_dir()
    
    def _get_csv_path(self, for_date: date = None) -> Path:
        """Get the CSV file path for a specific date."""
        if for_date is None:
            for_date = date.today()
        filename = f"{for_date.strftime('%Y-%m-%d')}.csv"
        return self.worklog_dir / filename
    
    def _ensure_csv_exists(self, csv_path: Path) -> None:
        """Create CSV file with headers if it doesn't exist."""
        if not csv_path.exists():
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADERS)
    
    def get_last_end_time(self, for_date: date = None) -> Optional[str]:
        """Get the end_time of the last entry for the given date."""
        entries = self.get_entries(for_date)
        if entries:
            return entries[-1].end_time
        return None
    
    def get_last_project(self) -> Optional[str]:
        """Get the project from the most recent entry."""
        entries = self.get_entries()
        if entries:
            return entries[-1].project
        return None
    
    def get_last_task_type(self) -> Optional[str]:
        """Get the task type from the most recent entry."""
        entries = self.get_entries()
        if entries:
            return entries[-1].task_type
        return None
    
    def get_all_projects(self) -> List[str]:
        """Get a list of all unique projects used."""
        projects = set()
        # Check last 30 days of files
        for i in range(30):
            try:
                from datetime import timedelta
                check_date = date.today() - timedelta(days=i)
                entries = self.get_entries(check_date)
                for entry in entries:
                    if entry.project:
                        projects.add(entry.project)
            except:
                continue
        return sorted(list(projects))
    
    def save_entry(self, project: str, task_type: str, description: str) -> LogEntry:
        """
        Save a new work log entry.
        Automatically calculates start_time from previous entry's end_time.
        """
        today = date.today()
        now = datetime.now()
        
        csv_path = self._get_csv_path(today)
        self._ensure_csv_exists(csv_path)
        
        # Calculate start time
        last_end_time = self.get_last_end_time(today)
        if last_end_time:
            start_time = last_end_time
        else:
            # First entry of the day - use current time minus interval as estimate
            from config import REMINDER_INTERVAL_MINUTES
            from datetime import timedelta
            start_dt = now - timedelta(minutes=REMINDER_INTERVAL_MINUTES)
            start_time = start_dt.strftime('%H:%M')
        
        end_time = now.strftime('%H:%M')
        date_str = today.strftime('%Y-%m-%d')
        
        entry = LogEntry(
            date=date_str,
            start_time=start_time,
            end_time=end_time,
            project=project,
            task_type=task_type,
            description=description
        )
        
        # Append to CSV (crash-safe with flush)
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry.date,
                entry.start_time,
                entry.end_time,
                entry.project,
                entry.task_type,
                entry.description
            ])
            f.flush()
            os.fsync(f.fileno())
        
        return entry
    
    def get_entries(self, for_date: date = None) -> List[LogEntry]:
        """Get all entries for a specific date."""
        csv_path = self._get_csv_path(for_date)
        
        if not csv_path.exists():
            return []
        
        entries = []
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    entry = LogEntry(
                        date=row['date'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        project=row['project'],
                        task_type=row['task_type'],
                        description=row['description']
                    )
                    entries.append(entry)
                except KeyError:
                    continue  # Skip malformed rows
        
        return entries
    
    def get_summary(self, for_date: date = None) -> Dict[str, Dict[str, dict]]:
        """
        Get a summary of entries grouped by Project and Task Type.
        Returns: {project: {task_type: {'minutes': int, 'descriptions': [str]}}}
        """
        entries = self.get_entries(for_date)
        summary = {}
        
        for entry in entries:
            # Calculate duration in minutes
            try:
                start = datetime.strptime(entry.start_time, '%H:%M')
                end = datetime.strptime(entry.end_time, '%H:%M')
                duration_minutes = int((end - start).total_seconds() / 60)
                if duration_minutes < 0:
                    duration_minutes = 0
            except ValueError:
                duration_minutes = 0
            
            project = entry.project or "No Project"
            task_type = entry.task_type or "Other"
            
            if project not in summary:
                summary[project] = {}
            
            if task_type not in summary[project]:
                summary[project][task_type] = {
                    'minutes': 0,
                    'descriptions': []
                }
            
            summary[project][task_type]['minutes'] += duration_minutes
            if entry.description:
                summary[project][task_type]['descriptions'].append(entry.description)
        
        return summary
    
    def format_summary(self, for_date: date = None) -> str:
        """Format the summary as human-readable text."""
        summary = self.get_summary(for_date)
        
        if not summary:
            return "No entries logged today."
        
        lines = []
        for project in sorted(summary.keys()):
            for task_type in sorted(summary[project].keys()):
                data = summary[project][task_type]
                hours = data['minutes'] // 60
                minutes = data['minutes'] % 60
                
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"
                
                lines.append(f"{project} – {task_type} – {time_str}")
                
                for desc in data['descriptions']:
                    lines.append(f"  • {desc}")
                
                lines.append("")  # Empty line between groups
        
        return "\n".join(lines).strip()
