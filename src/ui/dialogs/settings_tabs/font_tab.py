"""Font Settings Tab - Typography configuration."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox)
from PySide6.QtCore import Qt


def create_font_tab(dialog) -> QWidget:
    """Create Font selection tab.
    
    Args:
        dialog: Parent SettingsDialog instance
    
    Returns:
        QWidget containing the Font tab UI
    """
    from src.data.models import FONT_PRESETS
    
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(20)
    
    # Header
    header = QLabel("🔤 Cấu hình Font chữ")
    header.setStyleSheet("font-size: 16px; font-weight: 600;")
    layout.addWidget(header)
    
    desc = QLabel("Chọn font chữ cho tiêu đề và nội dung slide.")
    desc.setStyleSheet("color: #64748B;")
    layout.addWidget(desc)
    
    # Preset dropdown
    preset_layout = QHBoxLayout()
    preset_label = QLabel("Bộ font có sẵn:")
    preset_label.setFixedWidth(140)
    preset_layout.addWidget(preset_label)
    
    dialog.font_preset_combo = QComboBox()
    dialog.font_preset_combo.setMinimumWidth(200)
    for preset in FONT_PRESETS:
        dialog.font_preset_combo.addItem(
            f"{preset.display_name} ({preset.heading_font} / {preset.body_font})",
            preset.name
        )
    dialog.font_preset_combo.currentIndexChanged.connect(dialog._on_font_preset_changed)
    preset_layout.addWidget(dialog.font_preset_combo)
    preset_layout.addStretch()
    layout.addLayout(preset_layout)
    
    # Separator
    layout.addSpacing(10)
    sep_label = QLabel("─── hoặc tùy chỉnh riêng ───")
    sep_label.setStyleSheet("color: #64748B; font-size: 12px;")
    sep_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(sep_label)
    layout.addSpacing(10)
    
    # Heading font
    heading_layout = QHBoxLayout()
    heading_label = QLabel("Font tiêu đề:")
    heading_label.setFixedWidth(140)
    heading_layout.addWidget(heading_label)
    
    dialog.heading_font_combo = QComboBox()
    dialog.heading_font_combo.setMinimumWidth(200)
    dialog.heading_font_combo.setEditable(True)
    all_fonts = sorted(set(f.heading_font for f in FONT_PRESETS) | set(f.body_font for f in FONT_PRESETS))
    for font in all_fonts:
        dialog.heading_font_combo.addItem(font)
    heading_layout.addWidget(dialog.heading_font_combo)
    heading_layout.addStretch()
    layout.addLayout(heading_layout)
    
    # Body font
    body_layout = QHBoxLayout()
    body_label = QLabel("Font nội dung:")
    body_label.setFixedWidth(140)
    body_layout.addWidget(body_label)
    
    dialog.body_font_combo = QComboBox()
    dialog.body_font_combo.setMinimumWidth(200)
    dialog.body_font_combo.setEditable(True)
    for font in all_fonts:
        dialog.body_font_combo.addItem(font)
    body_layout.addWidget(dialog.body_font_combo)
    body_layout.addStretch()
    layout.addLayout(body_layout)
    
    # Preview
    layout.addSpacing(20)
    preview_label = QLabel("Xem trước:")
    preview_label.setStyleSheet("font-size: 14px; font-weight: 600;")
    layout.addWidget(preview_label)
    
    dialog.font_preview = QLabel("Tiêu đề Slide\nNội dung slide mẫu với font đã chọn.")
    dialog.font_preview.setStyleSheet("""
        background: #1E293B;
        padding: 20px;
        border-radius: 8px;
        font-size: 14px;
    """)
    dialog.font_preview.setMinimumHeight(80)
    layout.addWidget(dialog.font_preview)
    
    layout.addStretch()
    return tab
