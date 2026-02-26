"""Wizard Dialog - Collect user preferences before generation."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QRadioButton, QButtonGroup,
                               QFrame, QGridLayout)
from PySide6.QtCore import Qt


class WizardDialog(QDialog):
    """Dialog to customize generation preferences."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tùy chỉnh định hướng")
        self.setFixedWidth(500)
        self.setup_ui()
        self._load_saved_preferences()
    
    def _load_saved_preferences(self):
        """Load previously saved preferences from config."""
        try:
            from src.data.config_manager import ConfigManager
            config = ConfigManager()
            
            audience_idx = config.get("wizard_preferences.audience_index", 0)
            tone_idx = config.get("wizard_preferences.tone_index", 0)
            style_id = config.get("wizard_preferences.style_id", 2)
            
            # Set combo boxes
            if 0 <= audience_idx < self.audience_combo.count():
                self.audience_combo.setCurrentIndex(audience_idx)
            if 0 <= tone_idx < self.tone_combo.count():
                self.tone_combo.setCurrentIndex(tone_idx)
            
            # Set radio button
            btn = self.style_bg.button(style_id)
            if btn:
                btn.setChecked(True)
        except Exception:
            pass  # Silent fail - use defaults
        
    def setup_ui(self):
        """Setup the wizard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("🎯 Bạn muốn slide như thế nào?")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(header)
        
        description = QLabel("Giúp AI hiểu rõ hơn để tạo nội dung đúng ý bạn.")
        description.setStyleSheet("color: #94A3B8; margin-bottom: 10px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # === Section 1: Audience & Tone ===
        ctx_group = QFrame()
        ctx_group.setObjectName("card")
        ctx_group.setStyleSheet("""
            QFrame#card {
                background-color: #1E293B;
                border-radius: 8px;
                border: 1px solid #334155;
            }
        """)
        ctx_layout = QGridLayout(ctx_group)
        ctx_layout.setContentsMargins(16, 16, 16, 16)
        ctx_layout.setSpacing(12)
        
        # Audience
        ctx_layout.addWidget(QLabel("👥 Đối tượng xem:"), 0, 0)
        self.audience_combo = QComboBox()
        self.audience_combo.addItems([
            "Trung tính (General)",
            "Ban lãnh đạo (Executives)", 
            "Team Kỹ thuật (Technical)",
            "Khách hàng / Đối tác (Clients)",
            "Học sinh / Sinh viên (Students)"
        ])
        ctx_layout.addWidget(self.audience_combo, 0, 1)
        
        # Tone
        ctx_layout.addWidget(QLabel("🎭 Giọng văn:"), 1, 0)
        self.tone_combo = QComboBox()
        self.tone_combo.addItems([
            "Chuyên nghiệp (Professional)",
            "Truyền cảm hứng (Inspiring)",
            "Thân thiện (Casual)",
            "Học thuật (Academic)",
            "Thuyết phục (Persuasive)"
        ])
        ctx_layout.addWidget(self.tone_combo, 1, 1)
        
        layout.addWidget(ctx_group)
        
        # === Section 2: Layout Style ===
        style_label = QLabel("🎨 Phong cách trình bày:")
        style_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(style_label)
        
        style_group = QFrame()
        style_group.setObjectName("card")
        style_group.setStyleSheet("""
            QFrame#card {
                background-color: #1E293B;
                border-radius: 8px;
                border: 1px solid #334155;
            }
        """)
        style_layout = QVBoxLayout(style_group)
        
        self.style_bg = QButtonGroup(self)
        
        self.rad_visual = QRadioButton("Nhiều hình ảnh (Visual Heavy)")
        self.rad_visual.setToolTip("Ít chữ, tập trung vào hình ảnh minh họa và thiết kế.")
        
        self.rad_balanced = QRadioButton("Cân bằng (Balanced)")
        self.rad_balanced.setToolTip("Kết hợp hài hòa giữa nội dung và hình ảnh.")
        self.rad_balanced.setChecked(True)
        
        self.rad_detailed = QRadioButton("Chi tiết (Text Heavy)")
        self.rad_detailed.setToolTip("Nhiều thông tin, số liệu, phù hợp để làm báo cáo/tài liệu đọc.")
        
        self.style_bg.addButton(self.rad_visual, 1)
        self.style_bg.addButton(self.rad_balanced, 2)
        self.style_bg.addButton(self.rad_detailed, 3)
        
        style_layout.addWidget(self.rad_visual)
        style_layout.addWidget(self.rad_balanced)
        style_layout.addWidget(self.rad_detailed)
        
        layout.addWidget(style_group)
        
        layout.addStretch()
        
        # === Footer Buttons ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setObjectName("secondaryBtn")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_create = QPushButton("✨ Tạo ngay")
        self.btn_create.setObjectName("primaryBtn")
        self.btn_create.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_create)
        
        layout.addLayout(btn_layout)

    def get_data(self) -> dict:
        """Get the selected preferences."""
        # Map audience index/text to internal value if needed, 
        # but passing the full string is fine for LLM for now.
        audience_map = {
            0: "General Audience",
            1: "Executives/C-Level",
            2: "Technical Experts",
            3: "Clients/Partners",
            4: "Students/Academic"
        }
        
        tone_map = {
            0: "Professional & Formal",
            1: "Inspiring & Energetic",
            2: "Casual & Friendly",
            3: "Academic & Detailed",
            4: "Persuasive & Sales-oriented"
        }
        
        style_map = {
            1: "Visual Heavy (Minimal text, focus on imagery)",
            2: "Balanced (Good mix of text and visuals)",
            3: "Text Heavy (Detailed information, reports)"
        }
        
        return {
            "audience": audience_map.get(self.audience_combo.currentIndex(), "General"),
            "tone": tone_map.get(self.tone_combo.currentIndex(), "Professional"),
            "style": style_map.get(self.style_bg.checkedId(), "Balanced")
        }
