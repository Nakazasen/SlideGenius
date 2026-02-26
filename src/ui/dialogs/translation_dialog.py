"""Translation Dialog - UI for translating slides."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                QLabel, QPushButton, QComboBox,
                                QListWidget, QListWidgetItem, QProgressBar,
                                QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, Signal, QThread
from src.data.models import Outline
from src.core.translation_service import TranslationService
from src.core.pptx_generator import PPTXGenerator
from pathlib import Path


class TranslationWorker(QThread):
    """Worker thread for translation."""
    finished = Signal(object)  # Translated Outline
    error = Signal(str)
    progress = Signal(int, int)  # current, total
    
    def __init__(self, service: TranslationService, outline: Outline, 
                 target_lang: str, slide_indices: list):
        super().__init__()
        self.service = service
        self.outline = outline
        self.target_lang = target_lang
        self.slide_indices = slide_indices
    
    def run(self):
        try:
            translated = self.service.translate_outline(
                self.outline, 
                self.target_lang,
                self.slide_indices
            )
            self.finished.emit(translated)
        except Exception as e:
            self.error.emit(str(e))


class TranslationDialog(QDialog):
    """Dialog for translating presentation slides."""
    
    def __init__(self, outline: Outline, parent=None):
        super().__init__(parent)
        self.outline = outline
        self.translated_outline = None
        self.service = TranslationService()
        self.worker = None
        
        self.setWindowTitle("🌐 Dịch Slide")
        self.setMinimumSize(500, 450)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("🌐 Dịch nội dung slide sang ngôn ngữ khác")
        header.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(header)
        
        # Language selector
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Dịch sang:")
        lang_label.setFixedWidth(100)
        lang_layout.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.setMinimumWidth(200)
        for source, target, display in self.service.get_language_pairs():
            self.lang_combo.addItem(display, (source, target))
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Slide selection
        layout.addSpacing(10)
        slides_header = QLabel("Chọn slide cần dịch:")
        slides_header.setStyleSheet("font-weight: 600;")
        layout.addWidget(slides_header)
        
        # Select all checkbox
        self.select_all_check = QCheckBox("Chọn tất cả")
        self.select_all_check.setChecked(True)
        self.select_all_check.stateChanged.connect(self._on_select_all_changed)
        layout.addWidget(self.select_all_check)
        
        # Slide list
        self.slide_list = QListWidget()
        self.slide_list.setAlternatingRowColors(True)
        self.slide_list.setMinimumHeight(150)
        
        for i, slide in enumerate(self.outline.slides):
            item = QListWidgetItem(f"{i + 1}. {slide.title}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, i)
            self.slide_list.addItem(item)
        
        layout.addWidget(self.slide_list)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #64748B;")
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        self.translate_btn = QPushButton("🌐 Dịch")
        self.translate_btn.setObjectName("primaryBtn")
        self.translate_btn.clicked.connect(self._on_translate)
        btn_layout.addWidget(self.translate_btn)
        
        self.export_btn = QPushButton("📤 Xuất file đã dịch")
        self.export_btn.setObjectName("primaryBtn")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._on_export)
        btn_layout.addWidget(self.export_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_select_all_changed(self, state):
        """Handle select all checkbox change."""
        check_state = Qt.Checked if state == Qt.Checked else Qt.Unchecked
        for i in range(self.slide_list.count()):
            self.slide_list.item(i).setCheckState(check_state)
    
    def _get_selected_indices(self) -> list:
        """Get list of selected slide indices."""
        indices = []
        for i in range(self.slide_list.count()):
            item = self.slide_list.item(i)
            if item.checkState() == Qt.Checked:
                indices.append(item.data(Qt.UserRole))
        return indices
    
    def _on_translate(self):
        """Start translation."""
        selected = self._get_selected_indices()
        if not selected:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ít nhất 1 slide để dịch!")
            return
        
        # Get target language
        lang_data = self.lang_combo.currentData()
        source_lang, target_lang = lang_data
        
        # Update UI
        self.translate_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText("Đang dịch...")
        
        # Start worker
        self.worker = TranslationWorker(
            self.service, self.outline, target_lang, selected
        )
        self.worker.finished.connect(self._on_translation_finished)
        self.worker.error.connect(self._on_translation_error)
        self.worker.start()
    
    def _on_translation_finished(self, translated: Outline):
        """Handle translation complete."""
        self.translated_outline = translated
        self.progress_bar.hide()
        self.translate_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        lang_data = self.lang_combo.currentData()
        _, target_lang = lang_data
        lang_name = {"vi": "Việt", "en": "Anh", "ja": "Nhật"}.get(target_lang, target_lang)
        
        self.status_label.setText(f"✅ Đã dịch xong sang tiếng {lang_name}! Nhấn 'Xuất file' để lưu.")
        self.status_label.setStyleSheet("color: #10B981; font-weight: 600;")
    
    def _on_translation_error(self, error: str):
        """Handle translation error."""
        self.progress_bar.hide()
        self.translate_btn.setEnabled(True)
        self.status_label.setText(f"❌ Lỗi: {error}")
        self.status_label.setStyleSheet("color: #EF4444;")
    
    def _on_export(self):
        """Export translated presentation."""
        if not self.translated_outline:
            return
        
        from PySide6.QtWidgets import QFileDialog
        from datetime import datetime
        
        # Generate default filename
        lang_data = self.lang_combo.currentData()
        _, target_lang = lang_data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in self.translated_outline.title if c.isalnum() or c in " -_")[:30]
        default_name = f"{safe_title}_{target_lang.upper()}_{timestamp}.pptx"
        
        # File dialog
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu bản dịch",
            default_name,
            "PowerPoint Files (*.pptx)"
        )
        
        if filepath:
            try:
                generator = PPTXGenerator()
                output_path = generator.generate(self.translated_outline, Path(filepath))
                QMessageBox.information(
                    self, 
                    "Thành công",
                    f"✅ Đã xuất bản dịch:\n{output_path}"
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xuất file: {e}")
