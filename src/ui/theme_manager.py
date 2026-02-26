"""Theme Manager - Light/Dark mode switching."""
from pathlib import Path
from PySide6.QtWidgets import QApplication
from src.data.config_manager import ConfigManager


class ThemeManager:
    """Manages application themes (Light/Dark mode)."""
    
    STYLES_DIR = Path(__file__).parent / "styles"
    
    def __init__(self):
        self.config = ConfigManager()
        self.current_theme = self.config.get("ui.theme", "dark")
    
    def apply_theme(self, theme: str = None) -> None:
        """Apply theme to the entire application.
        
        Args:
            theme: 'light' or 'dark'. If None, uses current theme.
        """
        if theme:
            self.current_theme = theme
            self.config.set("ui.theme", theme)
        
        style_file = self.STYLES_DIR / f"{self.current_theme}.qss"
        if style_file.exists():
            with open(style_file, 'r', encoding='utf-8') as f:
                qss = f.read()
                app = QApplication.instance()
                if app:
                    app.setStyleSheet(qss)
    
    def toggle_theme(self) -> str:
        """Toggle between light and dark theme.
        
        Returns:
            The new theme name.
        """
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        return new_theme
    
    def is_dark(self) -> bool:
        """Check if current theme is dark."""
        return self.current_theme == "dark"
    
    def get_theme(self) -> str:
        """Get current theme name."""
        return self.current_theme
