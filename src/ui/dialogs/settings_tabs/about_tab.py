"""About Tab - Application info and credits."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


def create_about_tab(dialog) -> QWidget:
    """Create about tab.
    
    Args:
        dialog: Parent SettingsDialog instance
    
    Returns:
        QWidget containing the About tab UI
    """
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setAlignment(Qt.AlignCenter)
    
    icon = QLabel("🎯")
    icon.setStyleSheet("font-size: 48px;")
    icon.setAlignment(Qt.AlignCenter)
    layout.addWidget(icon)
    
    name = QLabel("Tạo Slide PowerPoint\ntự động bằng AI")
    name.setStyleSheet("font-size: 22px; font-weight: bold;")
    name.setAlignment(Qt.AlignCenter)
    layout.addWidget(name)
    
    version = QLabel("Phiên bản 1.0.0")
    version.setStyleSheet("color: #64748B;")
    version.setAlignment(Qt.AlignCenter)
    layout.addWidget(version)
    
    layout.addSpacing(20)
    
    # Credits section
    credits_title = QLabel("👤 Tác giả")
    credits_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #8B5CF6;")
    credits_title.setAlignment(Qt.AlignCenter)
    layout.addWidget(credits_title)
    
    author = QLabel("Bùi Đức Vinh")
    author.setStyleSheet("font-size: 16px; font-weight: bold;")
    author.setAlignment(Qt.AlignCenter)
    layout.addWidget(author)
    
    dept = QLabel("Phòng phát triển hệ thống Chế tạo")
    dept.setStyleSheet("color: #94A3B8; font-size: 13px;")
    dept.setAlignment(Qt.AlignCenter)
    layout.addWidget(dept)
    
    layout.addSpacing(20)
    
    # Open Logs Button
    log_btn = QPushButton("📂 Mở thư mục Logs")
    log_btn.setObjectName("secondaryBtn")
    log_btn.setCursor(Qt.PointingHandCursor)
    log_btn.clicked.connect(dialog._open_logs)
    layout.addWidget(log_btn)
    
    layout.addStretch()
    return tab
