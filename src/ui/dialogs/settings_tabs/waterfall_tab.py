"""Waterfall Strategy Tab - Model fallback configuration."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget


def create_waterfall_tab(dialog) -> QWidget:
    """Create Waterfall Strategy configuration tab.
    
    Args:
        dialog: Parent SettingsDialog instance
    
    Returns:
        QWidget containing the Waterfall tab UI
    """
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setSpacing(10)
    
    # Description
    desc = QLabel("Cấu hình chiến lược 'Thác nước' (Waterfall Strategy).\n"
                  "Khi model ưu tiên gặp lỗi, hệ thống sẽ tự động chuyển sang model tiếp theo.")
    desc.setWordWrap(True)
    desc.setStyleSheet("color: #64748B; margin-bottom: 10px;")
    layout.addWidget(desc)
    
    # Model List
    dialog.model_list = QListWidget()
    dialog.model_list.setAlternatingRowColors(True)
    layout.addWidget(dialog.model_list)
    
    # Hint
    hint = QLabel("💡 Tip: Bỏ chọn các model bạn không muốn sử dụng (ví dụ các model preview không ổn định).")
    hint.setStyleSheet("font-size: 11px; color: #94A3B8; font-style: italic;")
    layout.addWidget(hint)
    
    return tab
