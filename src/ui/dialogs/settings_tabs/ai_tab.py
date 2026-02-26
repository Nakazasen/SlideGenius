"""AI Settings Tab - API Keys and Generation Options."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSlider, QPlainTextEdit)
from PySide6.QtCore import Qt


def create_ai_tab(dialog) -> QWidget:
    """Create AI settings tab.
    
    Args:
        dialog: Parent SettingsDialog instance (for accessing shared state)
    
    Returns:
        QWidget containing the AI tab UI
    """
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(20)
    
    # API Key section
    api_section = QLabel("Cấu hình API")
    api_section.setStyleSheet("font-size: 16px; font-weight: 600;")
    layout.addWidget(api_section)
    
    # API Key input
    key_layout = QVBoxLayout()
    key_label = QLabel("Danh sách Khóa API Gemini (Mỗi dòng 1 key):")
    key_layout.addWidget(key_label)
    
    dialog.api_keys_input = QPlainTextEdit()
    dialog.api_keys_input.setPlaceholderText("Dán danh sách API keys vào đây...\nKey 1\nKey 2\n...")
    dialog.api_keys_input.setMinimumHeight(100)
    dialog.api_keys_input.setStyleSheet("font-family: monospace;")
    key_layout.addWidget(dialog.api_keys_input)
    
    layout.addLayout(key_layout)
    
    # Get API key link
    link_layout = QHBoxLayout()
    link_layout.addSpacing(124)
    get_key_btn = QPushButton("🔗 Lấy khóa API miễn phí từ Google AI Studio")
    get_key_btn.setStyleSheet("color: #60A5FA; background: transparent; text-align: left; padding: 0; border: none;")
    get_key_btn.setCursor(Qt.PointingHandCursor)
    get_key_btn.clicked.connect(dialog._open_api_link)
    link_layout.addWidget(get_key_btn)
    link_layout.addStretch()
    layout.addLayout(link_layout)
    
    # Test connection
    test_layout = QHBoxLayout()
    test_layout.addSpacing(124)
    dialog.test_btn = QPushButton("🔌 Kiểm tra kết nối")
    dialog.test_btn.clicked.connect(dialog._test_connection)
    test_layout.addWidget(dialog.test_btn)
    
    dialog.test_result = QLabel("")
    test_layout.addWidget(dialog.test_result)
    test_layout.addStretch()
    layout.addLayout(test_layout)
    
    # Waterfall Info
    layout.addSpacing(10)
    strategy_label = QLabel("Chiến lược Model:")
    strategy_label.setStyleSheet("font-size: 16px; font-weight: 600;")
    layout.addWidget(strategy_label)
    
    info_layout = QHBoxLayout()
    info_icon = QLabel("🌊")
    info_icon.setStyleSheet("font-size: 24px;")
    info_layout.addWidget(info_icon)
    
    info_text = QLabel("Hệ thống đang sử dụng <b>Waterfall Strategy</b> với 16 models.\n"
                       "Tự động chuyển model khác nếu gặp lỗi.")
    info_text.setWordWrap(True)
    info_text.setStyleSheet("color: #64748B;")
    info_layout.addWidget(info_text, 1)
    layout.addLayout(info_layout)
    
    # Generation options
    layout.addSpacing(20)
    gen_section = QLabel("Tùy chọn tạo nội dung")
    gen_section.setStyleSheet("font-size: 16px; font-weight: 600;")
    layout.addWidget(gen_section)
    
    creativity_layout = QHBoxLayout()
    creativity_label = QLabel("Độ sáng tạo:")
    creativity_label.setFixedWidth(120)
    creativity_layout.addWidget(creativity_label)
    
    dialog.creativity_slider = QSlider(Qt.Horizontal)
    dialog.creativity_slider.setRange(0, 100)
    dialog.creativity_slider.setFixedWidth(200)
    creativity_layout.addWidget(dialog.creativity_slider)
    
    dialog.creativity_value = QLabel("70%")
    dialog.creativity_value.setFixedWidth(40)
    dialog.creativity_slider.valueChanged.connect(
        lambda v: dialog.creativity_value.setText(f"{v}%")
    )
    creativity_layout.addWidget(dialog.creativity_value)
    creativity_layout.addStretch()
    layout.addLayout(creativity_layout)
    
    layout.addStretch()
    return tab
