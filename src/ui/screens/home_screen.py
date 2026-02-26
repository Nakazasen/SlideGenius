"""Home Screen - Main slide creation view."""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

from src.ui.components.input_panel import InputPanel
from src.ui.components.outline_editor import OutlineEditor


class HomeScreen(QWidget):
    """Main screen for creating new slides."""
    
    # Signals to communicate with main app
    generate_clicked = Signal(str, int)  # prompt, num_slides
    express_clicked = Signal(str, int, str) # prompt, num_slides, template_id
    export_clicked = Signal()
    translate_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the home screen UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        # Input panel
        self.input_panel = InputPanel()
        self.input_panel.generate_clicked.connect(self.generate_clicked.emit)
        self.input_panel.express_clicked.connect(self.express_clicked.emit)
        layout.addWidget(self.input_panel)
        
        # Outline editor
        self.outline_editor = OutlineEditor()
        self.outline_editor.export_clicked.connect(self.export_clicked.emit)
        self.outline_editor.translate_clicked.connect(self.translate_clicked.emit)
        layout.addWidget(self.outline_editor, 1)
    
    def set_loading(self, loading: bool):
        """Set loading state on input panel."""
        self.input_panel.set_loading(loading)
    
    def display_outline(self, outline):
        """Display generated outline."""
        self.outline_editor.set_outline(outline)
    
    def get_outline(self):
        """Get current outline from editor."""
        return self.outline_editor.get_outline()
    
    def clear_outline(self):
        """Clear the outline editor."""
        self.outline_editor.clear()
