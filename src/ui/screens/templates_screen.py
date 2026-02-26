"""Templates Screen - Template library with previews."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGridLayout,
                                QPushButton, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from src.data.config_manager import ConfigManager


class TemplateCard(QFrame):
    """Individual template card with preview."""
    
    clicked = Signal(str, str)  # template_id, template_name
    
    def __init__(self, template_id: str, name: str, color: str, description: str, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.name = name
        self.color = color
        self.description = description
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup card UI."""
        self.setObjectName("templateCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame#templateCard {{
                background: #1E293B;
                border-radius: 12px;
                border: 2px solid transparent;
                padding: 16px;
            }}
            QFrame#templateCard:hover {{
                border: 2px solid {self.color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Color preview bar
        color_bar = QWidget()
        color_bar.setFixedHeight(80)
        color_bar.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {self.color}, 
                stop:1 {self.color}88
            );
            border-radius: 8px;
        """)
        layout.addWidget(color_bar)
        
        # Template name
        name_label = QLabel(self.name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label)
        
        # Description
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Select button
        select_btn = QPushButton("Chọn mẫu này")
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self.color}DD;
            }}
        """)
        select_btn.clicked.connect(lambda: self.clicked.emit(self.template_id, self.name))
        layout.addWidget(select_btn)
    
    def mousePressEvent(self, event):
        """Handle click on card."""
        self.clicked.emit(self.template_id, self.name)
        super().mousePressEvent(event)


class TemplatesScreen(QWidget):
    """Screen showing template library with previews."""
    
    template_selected = Signal(str, str)  # template_id, template_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the templates screen UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Header
        title = QLabel("🎨 Thư viện Mẫu Slide")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Chọn một mẫu để áp dụng cho slide của bạn. Mẫu sẽ được lưu cho các lần tạo tiếp theo.")
        desc.setStyleSheet("color: #64748B; margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Current selection
        self.current_label = QLabel()
        self.current_label.setStyleSheet("color: #10B981; font-weight: bold;")
        layout.addWidget(self.current_label)
        self._update_current_label()
        
        # Templates grid
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        
        templates = [
            ("modern_blue", "Xanh Hiện Đại", "#3B82F6", "Phong cách doanh nghiệp, chuyên nghiệp"),
            ("creative_orange", "Cam Sáng Tạo", "#F97316", "Sáng tạo, năng động, phù hợp startup"),
            ("minimal_gray", "Xám Tối Giản", "#64748B", "Tối giản, thanh lịch, dễ đọc"),
            ("nature_green", "Xanh Thiên Nhiên", "#10B981", "Tự nhiên, thân thiện môi trường"),
            ("purple_gradient", "Tím Gradient", "#8B5CF6", "Hiện đại, công nghệ, sáng tạo"),
        ]
        
        for i, (tid, name, color, desc) in enumerate(templates):
            card = TemplateCard(tid, name, color, desc)
            card.clicked.connect(self._on_template_selected)
            row = i // 3
            col = i % 3
            grid_layout.addWidget(card, row, col)
        
        layout.addWidget(grid_widget)
        layout.addStretch()
    
    def _update_current_label(self):
        """Update the current selection label."""
        current = self.config.get("template.selected", "modern_blue")
        names = {
            "modern_blue": "Xanh Hiện Đại",
            "creative_orange": "Cam Sáng Tạo", 
            "minimal_gray": "Xám Tối Giản",
            "nature_green": "Xanh Thiên Nhiên",
            "purple_gradient": "Tím Gradient"
        }
        self.current_label.setText(f"✅ Đang sử dụng: {names.get(current, current)}")
    
    def _on_template_selected(self, template_id: str, name: str):
        """Handle template selection."""
        self.config.set("template.selected", template_id)
        self._update_current_label()
        self.template_selected.emit(template_id, name)
