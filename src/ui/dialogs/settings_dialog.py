"""Settings Dialog - Main dialog that composes all settings tabs."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                                QPushButton, QListWidgetItem)
from PySide6.QtCore import Qt, QThread, Signal
from src.data.config_manager import ConfigManager
from src.core.model_cascade import ModelCascade


class TestConnectionWorker(QThread):
    """Worker thread to test API connection without blocking UI."""
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, keys: list):
        super().__init__()
        self.keys = keys
    
    def run(self):
        from src.data.config_manager import ConfigManager
        from src.core.ai_service import AIService
        
        config = ConfigManager()
        old_keys = config.get("api.gemini_keys", [])
        
        try:
            config.set("api.gemini_keys", self.keys)
            ai = AIService()
            ai.reconfigure()
            success, message = ai.test_connection()
            
            if not success:
                config.set("api.gemini_keys", old_keys)
            
            self.finished.emit(success, message)
        except Exception as e:
            config.set("api.gemini_keys", old_keys)
            self.finished.emit(False, str(e))


class SettingsDialog(QDialog):
    """Settings dialog for configuring the application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.setWindowTitle("⚙️ Cài đặt")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        # Import tab factories
        from src.ui.dialogs.settings_tabs import (
            create_ai_tab, create_font_tab, create_waterfall_tab, create_about_tab
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Tab widget - using extracted tab modules
        tabs = QTabWidget()
        tabs.addTab(create_ai_tab(self), "🤖 Cài đặt AI")
        tabs.addTab(create_font_tab(self), "🔤 Font chữ")
        tabs.addTab(create_waterfall_tab(self), "🌊 Chiến lược Waterfall")
        tabs.addTab(create_about_tab(self), "ℹ️ Giới thiệu")
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Lưu")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_font_preset_changed(self, index: int):
        """Handle font preset selection."""
        from src.data.models import FONT_PRESETS
        if 0 <= index < len(FONT_PRESETS):
            preset = FONT_PRESETS[index]
            self.heading_font_combo.setCurrentText(preset.heading_font)
            self.body_font_combo.setCurrentText(preset.body_font)
    
    def _open_logs(self):
        """Open logs directory in explorer."""
        import os
        from src.utils.logger import LOG_DIR
        
        log_path = os.path.abspath(LOG_DIR)
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
            
        os.startfile(log_path)
    
    def _load_settings(self):
        """Load current settings into UI."""
        # Load keys list
        keys = self.config.get("api.gemini_keys", [])
        if not keys and self.config.get("api.gemini_key"):
            keys = [self.config.get("api.gemini_key")]
             
        self.api_keys_input.setPlainText("\n".join(keys))
        
        creativity = self.config.get("generation.creativity_level", 70)
        self.creativity_slider.setValue(creativity)
        
        # Load Waterfall Strategy
        ModelCascade() 
        strategy = self.config.get("api.waterfall_strategy", [])
        
        self.model_list.clear()
        for idx, model in enumerate(strategy):
            item_text = f"{idx + 1}. {model['model_id']} (Timeout: {model['timeout']}s)"
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            check_state = Qt.Checked if model['is_active'] else Qt.Unchecked
            item.setCheckState(check_state)
            item.setData(Qt.UserRole, model)
            self.model_list.addItem(item)
        
        # Load Font settings
        from src.data.models import FONT_PRESETS
        current_preset = self.config.get("fonts.preset", "modern")
        heading_font = self.config.get("fonts.heading_font", "Montserrat")
        body_font = self.config.get("fonts.body_font", "Open Sans")
        
        for i, preset in enumerate(FONT_PRESETS):
            if preset.name == current_preset:
                self.font_preset_combo.setCurrentIndex(i)
                break
        
        self.heading_font_combo.setCurrentText(heading_font)
        self.body_font_combo.setCurrentText(body_font)
    
    def _save_settings(self):
        """Save settings to config."""
        text = self.api_keys_input.toPlainText()
        keys = [k.strip() for k in text.splitlines() if k.strip()]
        
        self.config.set("api.gemini_keys", keys)
        if keys:
            self.config.set("api.gemini_key", keys[0])
        else:
            self.config.set("api.gemini_key", "")
            
        self.config.set("generation.creativity_level", self.creativity_slider.value())
        
        # Save Waterfall Strategy
        new_strategy = []
        for i in range(self.model_list.count()):
            item = self.model_list.item(i)
            model_data = item.data(Qt.UserRole)
            model_data['is_active'] = (item.checkState() == Qt.Checked)
            new_strategy.append(model_data)
            
        self.config.set("api.waterfall_strategy", new_strategy)
        
        # Save Font settings
        preset_name = self.font_preset_combo.currentData()
        heading_font = self.heading_font_combo.currentText()
        body_font = self.body_font_combo.currentText()
        
        self.config.set("fonts.preset", preset_name)
        self.config.set("fonts.heading_font", heading_font)
        self.config.set("fonts.body_font", body_font)
        
        self.accept()
    
    def _test_connection(self):
        """Test API connection in background thread."""
        text = self.api_keys_input.toPlainText()
        keys = [k.strip() for k in text.splitlines() if k.strip()]
        
        if not keys:
            self.test_result.setText("❌ Nhập ít nhất 1 API key")
            self.test_result.setStyleSheet("color: #EF4444;")
            return
        
        self.test_btn.setEnabled(False)
        self.test_result.setText("⏳ Đang test...")
        self.test_result.setStyleSheet("color: #94A3B8;")
        
        self._test_worker = TestConnectionWorker(keys)
        self._test_worker.finished.connect(self._on_test_finished)
        self._test_worker.start()
    
    def _on_test_finished(self, success: bool, message: str):
        """Handle test connection result from worker."""
        self.test_btn.setEnabled(True)
        
        if success:
            self.test_result.setText("✅ " + message)
            self.test_result.setStyleSheet("color: #10B981;")
        else:
            self.test_result.setText("❌ " + message)
            self.test_result.setStyleSheet("color: #EF4444;")
    
    def _open_api_link(self):
        """Open Google AI Studio link."""
        import webbrowser
        webbrowser.open("https://aistudio.google.com/app/apikey")
