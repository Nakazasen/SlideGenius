"""Outline Editor Component - Display and edit generated outline."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                                QLabel, QPushButton, QFrame, QTextEdit, QLineEdit)
from PySide6.QtCore import Signal, Qt
from src.data.models import Outline, SlideItem


class SlideCard(QFrame):
    """Card representing a single slide in the outline."""
    
    edit_clicked = Signal(int)
    delete_clicked = Signal(int)
    
    def __init__(self, index: int, slide: SlideItem):
        super().__init__()
        self.index = index
        self.slide = slide
        self.setProperty("class", "card")
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup card UI."""
        self.setStyleSheet("""
            SlideCard {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px;
            }
            SlideCard:hover {
                border-color: #8B5CF6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Header row
        header = QHBoxLayout()
        
        # Slide number
        num_label = QLabel(f"Slide {self.index + 1}")
        num_label.setStyleSheet("font-size: 12px; color: #8B5CF6; font-weight: 600;")
        header.addWidget(num_label)
        
        # Type badge
        type_label = QLabel(f"[{self.slide.slide_type.value}]")
        type_label.setStyleSheet("font-size: 11px; color: #64748B;")
        header.addWidget(type_label)
        
        # Image indicator
        if self.slide.image_path:
            img_indicator = QLabel(" 🖼️")
            img_indicator.setToolTip("Slide này có hình ảnh")
            header.addWidget(img_indicator)
        
        header.addStretch()
        
        # Delete button
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("background: transparent; border: none;")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        header.addWidget(delete_btn)
        
        layout.addLayout(header)
        
        # Title
        title = QLabel(self.slide.title)
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Content bullets
        if self.slide.content:
            for point in self.slide.content[:4]:  # Max 4 points shown
                bullet = QLabel(f"• {point}")
                bullet.setStyleSheet("font-size: 13px; color: #94A3B8; padding-left: 8px;")
                bullet.setWordWrap(True)
                layout.addWidget(bullet)
            
            if len(self.slide.content) > 4:
                more = QLabel(f"... và {len(self.slide.content) - 4} điểm nữa")
                more.setStyleSheet("font-size: 12px; color: #64748B; font-style: italic;")
                layout.addWidget(more)


class OutlineEditor(QWidget):
    """Editor for the generated presentation outline."""
    
    outline_changed = Signal()
    export_clicked = Signal()
    translate_clicked = Signal()  # NEW: Translation signal
    
    def __init__(self):
        super().__init__()
        self.outline = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        
        self.title_label = QLabel("📋 Dàn ý")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        self.slide_count = QLabel("")
        self.slide_count.setStyleSheet("color: #64748B;")
        header.addWidget(self.slide_count)
        
        layout.addLayout(header)
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 8, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()
        
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll, 1)
        
        # Action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        # Translate button
        self.translate_btn = QPushButton("🌐 Dịch slide")
        self.translate_btn.setObjectName("secondaryBtn")
        self.translate_btn.setMinimumHeight(44)
        self.translate_btn.clicked.connect(self.translate_clicked.emit)
        self.translate_btn.setVisible(False)
        btn_row.addWidget(self.translate_btn)
        
        # Export button
        self.export_btn = QPushButton("📥 Xuất PowerPoint")
        self.export_btn.setObjectName("primaryBtn")
        self.export_btn.setMinimumHeight(44)
        self.export_btn.clicked.connect(self.export_clicked.emit)
        self.export_btn.setVisible(False)
        btn_row.addWidget(self.export_btn)
        
        layout.addLayout(btn_row)
    
    def set_outline(self, outline: Outline):
        """Set the outline to display."""
        self.outline = outline
        self._refresh_cards()
    
    def _refresh_cards(self):
        """Refresh the slide cards display."""
        # Clear existing cards
        while self.cards_layout.count() > 1:  # Keep the stretch
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.outline:
            return
        
        # Update header
        self.title_label.setText(f"📋 {self.outline.title}")
        self.slide_count.setText(f"{self.outline.slide_count} slides")
        
        # Add cards
        for i, slide in enumerate(self.outline.slides):
            card = SlideCard(i, slide)
            card.delete_clicked.connect(self._on_delete_slide)
            self.cards_layout.insertWidget(i, card)
        
        # Show export button
        self.export_btn.setVisible(True)
        self.translate_btn.setVisible(True)
    
    def _on_delete_slide(self, index: int):
        """Handle slide deletion."""
        if self.outline and 0 <= index < len(self.outline.slides):
            self.outline.remove_slide(index)
            self._refresh_cards()
            self.outline_changed.emit()
    
    def get_outline(self) -> Outline:
        """Get the current outline."""
        return self.outline
    
    def clear(self):
        """Clear the editor."""
        self.outline = None
        self.title_label.setText("📋 Dàn ý")
        self.slide_count.setText("")
        self.export_btn.setVisible(False)
        
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
