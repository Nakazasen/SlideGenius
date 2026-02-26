"""Sidebar Navigation Component."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                                QLabel, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal


class Sidebar(QWidget):
    """Left sidebar navigation component."""
    
    # Signal emitted when navigation changes
    navigation_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.nav_buttons = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)
        
        # Logo
        logo = QLabel("🎯 Tạo Slide AI")
        logo.setObjectName("logo")
        layout.addWidget(logo)
        layout.addSpacing(24)
        
        # Navigation items
        nav_items = [
            ("home", "🏠  Trang chủ"),
            ("history", "📋  Lịch sử"),
            ("templates", "🎨  Mẫu Slide"),
        ]
        
        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._on_nav_click(k))
            self.nav_buttons[key] = btn
            layout.addWidget(btn)
        
        # Set home as default active
        self.nav_buttons["home"].setChecked(True)
        
        # Spacer to push settings to bottom
        layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        
        # Theme toggle
        self.theme_btn = QPushButton("🌙  Chế độ tối")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(lambda: self.navigation_changed.emit("toggle_theme"))
        layout.addWidget(self.theme_btn)
        
        layout.addSpacing(8)
        
        # Help button (NEW)
        help_btn = QPushButton("❓  Hướng dẫn")
        help_btn.setCursor(Qt.PointingHandCursor)
        help_btn.clicked.connect(lambda: self._on_nav_click("help"))
        self.nav_buttons["help"] = help_btn
        layout.addWidget(help_btn)
        
        layout.addSpacing(4)
        
        # Settings button
        settings_btn = QPushButton("⚙️  Cài đặt")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(lambda: self._on_nav_click("settings"))
        self.nav_buttons["settings"] = settings_btn
        layout.addWidget(settings_btn)
    
    def _on_nav_click(self, key: str):
        """Handle navigation button click."""
        # Uncheck all regular nav buttons
        for k, btn in self.nav_buttons.items():
            if k != "settings":  # Settings doesn't get checked state
                btn.setChecked(k == key)
        
        self.navigation_changed.emit(key)
    
    def update_theme_button(self, is_dark: bool):
        """Update theme button text based on current theme."""
        if is_dark:
            self.theme_btn.setText("🌙  Chế độ tối")
        else:
            self.theme_btn.setText("☀️  Chế độ sáng")
    
    def set_active(self, key: str):
        """Programmatically set active navigation item."""
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)


# Import Qt here to avoid circular imports
from PySide6.QtCore import Qt
