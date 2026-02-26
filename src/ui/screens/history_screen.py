"""History Screen - View past slide generations."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                                QListWidgetItem, QHBoxLayout, QPushButton,
                                QMessageBox)
from PySide6.QtCore import Qt, Signal
from src.data.database import DatabaseManager


class HistoryScreen(QWidget):
    """Screen showing history of generated slides."""
    
    # Signal when user wants to open a past outline
    outline_selected = Signal(dict)  # outline_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the history screen UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("📜 Lịch sử tạo Slide")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(self.refresh_history)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("Xem lại các bài thuyết trình đã tạo trước đây.")
        desc.setStyleSheet("color: #64748B; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.history_list, 1)
        
        # Empty state
        self.empty_label = QLabel("📭 Chưa có lịch sử nào.\nHãy tạo slide đầu tiên của bạn!")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #94A3B8; font-size: 16px;")
        self.empty_label.hide()
        layout.addWidget(self.empty_label)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        delete_btn = QPushButton("🗑️ Xóa mục đã chọn")
        delete_btn.setObjectName("dangerBtn")
        delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(delete_btn)
        
        open_btn = QPushButton("📂 Mở")
        open_btn.setObjectName("primaryBtn")
        open_btn.clicked.connect(self._open_selected)
        btn_layout.addWidget(open_btn)
        
        layout.addLayout(btn_layout)
    
    def refresh_history(self):
        """Load history from database."""
        self.history_list.clear()
        
        try:
            history = self.db.get_history()
            
            if not history:
                self.history_list.hide()
                self.empty_label.show()
                return
            
            self.empty_label.hide()
            self.history_list.show()
            
            for item in history:
                # item is a dict: {id, title, prompt, outline_json, template_name, output_path, slide_count, created_at}
                list_item = QListWidgetItem()
                list_item.setText(f"📊 {item['title']}\n   🕐 {item['created_at']} | 🎨 {item.get('template_name') or 'Default'}")
                list_item.setData(Qt.UserRole, item)
                self.history_list.addItem(list_item)
                
        except Exception as e:
            self.empty_label.setText(f"❌ Lỗi tải lịch sử: {str(e)}")
            self.empty_label.show()
            self.history_list.hide()
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double click on history item."""
        data = item.data(Qt.UserRole)
        if data:
            self.outline_selected.emit(data)
    
    def _open_selected(self):
        """Open selected history item."""
        current = self.history_list.currentItem()
        if current:
            self._on_item_double_clicked(current)
        else:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn một mục từ danh sách.")
    
    def _delete_selected(self):
        """Delete selected history item."""
        current = self.history_list.currentItem()
        if not current:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn một mục để xóa.")
            return
        
        data = current.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa '{data['title']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_history(data['id'])
                self.refresh_history()
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể xóa: {str(e)}")
    
    def showEvent(self, event):
        """Refresh history when screen is shown."""
        super().showEvent(event)
        self.refresh_history()
