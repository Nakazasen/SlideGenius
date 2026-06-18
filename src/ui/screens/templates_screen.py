"""Templates Screen - Template library with previews."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.data.config_manager import ConfigManager
from src.data.templates import TEMPLATE_LIST


class TemplateCard(QFrame):
    """Individual template card with preview."""

    clicked = Signal(str, str)

    def __init__(self, template_id: str, name: str, color: str, description: str, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.name = name
        self.color = color
        self.description = description
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("templateCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QFrame#templateCard {{
                background: #1E293B;
                border-radius: 12px;
                border: 2px solid transparent;
                padding: 16px;
            }}
            QFrame#templateCard:hover {{
                border: 2px solid {self.color};
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        color_bar = QWidget()
        color_bar.setFixedHeight(80)
        color_bar.setStyleSheet(
            f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {self.color},
                stop:1 {self.color}88
            );
            border-radius: 8px;
        """
        )
        layout.addWidget(color_bar)

        name_label = QLabel(self.name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label)

        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        select_btn = QPushButton("Chọn mẫu này")
        select_btn.setStyleSheet(
            f"""
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
        """
        )
        select_btn.clicked.connect(lambda: self.clicked.emit(self.template_id, self.name))
        layout.addWidget(select_btn)

    def mousePressEvent(self, event):
        self.clicked.emit(self.template_id, self.name)
        super().mousePressEvent(event)


class TemplatesScreen(QWidget):
    """Screen showing template library with previews."""

    template_selected = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Thư viện mẫu Slide")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("Chọn một theme business-grade để áp dụng cho các deck PowerPoint tiếp theo.")
        desc.setStyleSheet("color: #64748B; margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.current_label = QLabel()
        self.current_label.setStyleSheet("color: #10B981; font-weight: bold;")
        layout.addWidget(self.current_label)
        self._update_current_label()

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)

        for index, (template_id, name, color, description) in enumerate(TEMPLATE_LIST):
            card = TemplateCard(template_id, name, color, description)
            card.clicked.connect(self._on_template_selected)
            row = index // 2
            col = index % 2
            grid_layout.addWidget(card, row, col)

        layout.addWidget(grid_widget)
        layout.addStretch()

    def _update_current_label(self):
        current = self.config.get("template.selected", "executive_blue")
        names = {template_id: name for template_id, name, _, _ in TEMPLATE_LIST}
        self.current_label.setText(f"Đang sử dụng: {names.get(current, current)}")

    def _on_template_selected(self, template_id: str, name: str):
        self.config.set("template.selected", template_id)
        self._update_current_label()
        self.template_selected.emit(template_id, name)
