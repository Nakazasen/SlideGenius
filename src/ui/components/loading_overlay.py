"""Loading Overlay Widget - Show progress during generation."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import Qt, QTimer


class LoadingOverlay(QWidget):
    """Overlay widget showing loading progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("loadingOverlay")
        self._setup_ui()
        
        # Animation timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._animate_progress)
        self.current_step = 0
    
    def _setup_ui(self):
        """Setup overlay UI."""
        self.setStyleSheet("""
            #loadingOverlay {
                background-color: rgba(15, 23, 42, 0.95);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container
        container = QWidget()
        container.setFixedWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon = QLabel("🧠")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(icon)
        
        # Title
        self.title = QLabel("Đang tạo outline...")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F1F5F9;")
        self.title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.title)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #334155;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:0.5 #8B5CF6, stop:1 #F97316);
                border-radius: 4px;
            }
        """)
        container_layout.addWidget(self.progress)
        
        # Step label
        self.step_label = QLabel("Phân tích yêu cầu...")
        self.step_label.setStyleSheet("font-size: 14px; color: #94A3B8;")
        self.step_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.step_label)
        
        # Cancel button
        cancel_btn = QPushButton("⏹ Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #475569;
                color: #94A3B8;
                padding: 8px 24px;
                border-radius: 6px;
            }
            QPushButton:hover {
                border-color: #EF4444;
                color: #EF4444;
            }
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        container_layout.addWidget(cancel_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(container)
    
    def start(self):
        """Start loading animation."""
        self.current_step = 0
        self.progress.setValue(0)
        self.progress_timer.start(100)
        self.show()
    
    def stop(self):
        """Stop loading animation."""
        self.progress_timer.stop()
        self.hide()
    
    def _animate_progress(self):
        """Animate progress bar."""
        steps = [
            (25, "Phân tích yêu cầu..."),
            (50, "Tạo cấu trúc slide..."),
            (75, "Viết nội dung..."),
            (90, "Hoàn thiện outline..."),
        ]
        
        current = self.progress.value()
        if current < 90:
            self.progress.setValue(current + 1)
            
            for threshold, text in steps:
                if current >= threshold - 1 and current < threshold + 1:
                    self.step_label.setText(text)
                    break
