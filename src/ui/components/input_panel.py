"""Input Panel Component - Prompt input and file upload."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                QTextEdit, QPushButton, QLabel, QSpinBox, QComboBox)
from PySide6.QtCore import Signal, Qt
from src.data.templates import TEMPLATE_LIST


class InputPanel(QWidget):
    """Panel for entering prompt and controlling generation."""
    
    # Signals
    generate_clicked = Signal(str, int)  # prompt, num_slides
    express_clicked = Signal(str, int, str) # prompt, num_slides, template_id
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the input panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("✨ Tạo Slide mới")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # Prompt input
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Nhập ý tưởng slide của bạn...\n\n"
            "Ví dụ:\n"
            "• Báo cáo doanh thu quý 4 năm 2025\n"
            "• Giới thiệu sản phẩm mới cho team marketing\n"
            "• Bài thuyết trình về AI trong doanh nghiệp"
        )
        self.prompt_input.setMinimumHeight(120)
        self.prompt_input.setMaximumHeight(200)
        layout.addWidget(self.prompt_input)
        
        # Controls row
        controls = QHBoxLayout()
        controls.setSpacing(12)
        
        # Slide count
        slides_label = QLabel("Số slides:")
        controls.addWidget(slides_label)
        
        self.slides_spin = QSpinBox()
        self.slides_spin.setRange(1, 20)
        self.slides_spin.setValue(8)
        self.slides_spin.setFixedWidth(50)
        controls.addWidget(self.slides_spin)
        
        # Template Selector (For Express Mode)
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(120)
        for t_id, t_name, _, _ in TEMPLATE_LIST:
            self.template_combo.addItem(f"🎨 {t_name}", t_id)
        controls.addWidget(self.template_combo)
        
        controls.addStretch()
        
        # Generate button (Standard)
        self.generate_btn = QPushButton("📝 Dàn Ý")
        self.generate_btn.setToolTip("Tạo dàn ý trước để chỉnh sửa")
        self.generate_btn.clicked.connect(self._on_generate)
        controls.addWidget(self.generate_btn)
        
        # Express Button (New)
        self.express_btn = QPushButton("⚡ Tạo Ngay")
        self.express_btn.setObjectName("primaryBtn") # Make this the primary action
        self.express_btn.setMinimumWidth(100)
        self.express_btn.setToolTip("Tạo slide ngay lập tức, bỏ qua sửa dàn ý")
        self.express_btn.clicked.connect(self._on_express)
        controls.addWidget(self.express_btn)
        
        layout.addLayout(controls)
    
    def _on_generate(self):
        """Handle standard generate (Outline only)."""
        prompt = self.prompt_input.toPlainText().strip()
        if prompt:
            num_slides = self.slides_spin.value()
            self.generate_clicked.emit(prompt, num_slides)

    def _on_express(self):
        """Handle express generate (Skip outline review)."""
        prompt = self.prompt_input.toPlainText().strip()
        if prompt:
            num_slides = self.slides_spin.value()
            template_id = self.template_combo.currentData()
            self.express_clicked.emit(prompt, num_slides, template_id)
    
    def get_prompt(self) -> str:
        """Get current prompt text."""
        return self.prompt_input.toPlainText().strip()
    
    def set_loading(self, loading: bool, message: str = "⏳ Đang tạo..."):
        """Set loading state with custom message."""
        self.generate_btn.setEnabled(not loading)
        self.express_btn.setEnabled(not loading)
        self.template_combo.setEnabled(not loading)
        
        if loading:
            self.express_btn.setText(message)
        else:
            self.express_btn.setText("⚡ Tạo Ngay")
    
    def clear(self):
        """Clear the input."""
        self.prompt_input.clear()
