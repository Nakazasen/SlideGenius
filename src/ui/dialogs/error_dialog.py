"""Error Dialog - Show friendly error messages."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                QLabel, QPushButton, QTextEdit)
from PySide6.QtCore import Qt


class ErrorDialog(QDialog):
    """Dialog for showing error messages in a friendly way."""
    
    def __init__(self, title: str, message: str, details: str = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        self.details = details
        self.setWindowTitle("❌ Oops!")
        self.setMinimumSize(450, 250)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Icon
        icon = QLabel("😢")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Message
        msg_label = QLabel(self.message)
        msg_label.setStyleSheet("font-size: 14px; color: #94A3B8;")
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg_label)
        
        # Suggestions
        suggestions = QLabel(
            "💡 Gợi ý:\n"
            "• Kiểm tra kết nối internet\n"
            "• Xác nhận API key đúng\n"
            "• Thử lại sau vài giây"
        )
        suggestions.setStyleSheet("""
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            padding: 12px;
            color: #60A5FA;
            font-size: 13px;
        """)
        layout.addWidget(suggestions)
        
        # Details (collapsible)
        if self.details:
            self.details_toggle = QPushButton("📋 Xem chi tiết")
            self.details_toggle.setStyleSheet("background: transparent; color: #64748B;")
            self.details_toggle.setCursor(Qt.PointingHandCursor)
            self.details_toggle.clicked.connect(self._toggle_details)
            layout.addWidget(self.details_toggle)
            
            self.details_box = QTextEdit()
            self.details_box.setReadOnly(True)
            self.details_box.setPlainText(self.details)
            self.details_box.setMaximumHeight(100)
            self.details_box.setStyleSheet("""
                background: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                font-family: monospace;
                font-size: 12px;
                color: #94A3B8;
            """)
            self.details_box.hide()
            layout.addWidget(self.details_box)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        retry_btn = QPushButton("🔄 Thử lại")
        retry_btn.setObjectName("primaryBtn")
        retry_btn.clicked.connect(self.accept)
        btn_layout.addWidget(retry_btn)
        
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _toggle_details(self):
        """Toggle details visibility."""
        if self.details_box.isVisible():
            self.details_box.hide()
            self.details_toggle.setText("📋 Xem chi tiết")
        else:
            self.details_box.show()
            self.details_toggle.setText("📋 Ẩn chi tiết")
