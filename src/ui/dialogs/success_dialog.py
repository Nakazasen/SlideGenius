"""Success Dialog - Show export completion."""
from pathlib import Path
import subprocess
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                QLabel, QPushButton, QWidget)
from PySide6.QtCore import Qt


class SuccessDialog(QDialog):
    """Dialog shown after successful PPTX export."""
    
    def __init__(self, output_path: Path, slide_count: int, parent=None):
        super().__init__(parent)
        self.output_path = output_path
        self.slide_count = slide_count
        self.setWindowTitle("✅ Export Thành Công!")
        self.setMinimumSize(450, 300)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        # Success icon
        icon = QLabel("🎉")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        
        # Title
        title = QLabel("Tạo Slide Thành Công!")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Stats
        stats = QLabel(f"📊 {self.slide_count} slides đã được tạo")
        stats.setStyleSheet("font-size: 16px; color: #64748B;")
        stats.setAlignment(Qt.AlignCenter)
        layout.addWidget(stats)
        
        # File info
        file_info = QWidget()
        file_layout = QVBoxLayout(file_info)
        file_layout.setContentsMargins(16, 12, 16, 12)
        file_info.setStyleSheet("""
            background-color: #1E293B;
            border-radius: 8px;
        """)
        
        file_name = QLabel(f"📄 {self.output_path.name}")
        file_name.setStyleSheet("font-size: 14px; font-weight: 500;")
        file_layout.addWidget(file_name)
        
        file_path = QLabel(f"📁 {self.output_path.parent}")
        file_path.setStyleSheet("font-size: 12px; color: #64748B;")
        file_path.setWordWrap(True)
        file_layout.addWidget(file_path)
        
        layout.addWidget(file_info)
        
        layout.addSpacing(8)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        # Open folder
        folder_btn = QPushButton("📂 Mở Thư Mục")
        folder_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(folder_btn)
        
        # Open PowerPoint
        pptx_btn = QPushButton("📊 Mở PowerPoint")
        pptx_btn.setObjectName("primaryBtn")
        pptx_btn.clicked.connect(self._open_pptx)
        btn_layout.addWidget(pptx_btn)
        
        layout.addLayout(btn_layout)
        
        # New slide button
        new_btn = QPushButton("✨ Tạo Slide Mới")
        new_btn.clicked.connect(self.accept)
        layout.addWidget(new_btn)
    
    def _open_folder(self):
        """Open containing folder."""
        folder = self.output_path.parent
        if os.name == 'nt':  # Windows
            os.startfile(folder)
        else:
            subprocess.run(['open', folder])
    
    def _open_pptx(self):
        """Open the PPTX file."""
        if os.name == 'nt':  # Windows
            os.startfile(self.output_path)
        else:
            subprocess.run(['open', self.output_path])
        self.accept()
