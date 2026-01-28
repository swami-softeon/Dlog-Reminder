"""
Icon generator for Work Logger.
Creates a simple clock/log icon for the system tray.
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QRect
import sys
import os


def create_icon_pixmap(size: int = 64) -> QPixmap:
    """Create a simple icon pixmap for the application."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw background circle
    painter.setBrush(QColor(52, 152, 219))  # Nice blue color
    painter.setPen(Qt.NoPen)
    margin = size // 8
    painter.drawEllipse(margin, margin, size - 2*margin, size - 2*margin)
    
    # Draw clock hands or a simple "W" for Work
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Arial", size // 3, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "W")
    
    painter.end()
    return pixmap


def save_icon(path: str):
    """Save the icon to a file."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    pixmap = create_icon_pixmap(256)
    pixmap.save(path)
    print(f"Icon saved to: {path}")


if __name__ == "__main__":
    # Generate icon file
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    save_icon(icon_path)
