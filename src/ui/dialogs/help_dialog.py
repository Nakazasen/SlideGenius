"""Help Dialog - User guide and instructions."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton, QScrollArea,
                                QWidget, QFrame)
from PySide6.QtCore import Qt


class HelpDialog(QDialog):
    """Dialog showing detailed usage instructions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("❓ Hướng dẫn sử dụng")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("📖 Hướng dẫn sử dụng chi tiết")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)
        
        subtitle = QLabel("Phần mềm Tạo Slide PowerPoint tự động bằng AI")
        subtitle.setStyleSheet("color: #64748B; margin-bottom: 10px;")
        layout.addWidget(subtitle)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Section 1: API Key
        content_layout.addWidget(self._create_section(
            "🔑 Bước 1: Lấy API Key (Miễn phí)",
            [
                "1. Truy cập: https://aistudio.google.com/app/apikey",
                "2. Đăng nhập bằng tài khoản Google",
                "3. Nhấn 'Create API Key' → Chọn project",
                "4. Copy API Key vừa tạo",
                "5. Mở Settings (⚙️) → Dán vào ô 'API Key'",
                "6. Nhấn 'Kiểm tra kết nối' để xác nhận"
            ]
        ))
        
        # Section 2: Create Slides
        content_layout.addWidget(self._create_section(
            "✍️ Bước 2: Tạo Slide",
            [
                "1. Nhập chủ đề vào ô 'Nhập chủ đề...'",
                "   Ví dụ: 'Giới thiệu công ty ABC'",
                "2. Chọn số slide (5-15 slide)",
                "3. Nhấn nút '✨ Tạo Outline'",
                "4. Chờ AI tạo nội dung (~10-30 giây)",
                "5. Xem lại và chỉnh sửa nếu cần"
            ]
        ))
        
        # Section 3: Font Selection
        content_layout.addWidget(self._create_section(
            "🔤 Bước 3: Chọn Font chữ (Tùy chọn)",
            [
                "1. Mở Settings (⚙️) → Tab 'Font chữ'",
                "2. Chọn bộ font từ danh sách có sẵn",
                "   Hoặc tùy chỉnh riêng:",
                "   - Font tiêu đề: cho các heading",
                "   - Font nội dung: cho nội dung chính",
                "3. Nhấn 'Lưu' để áp dụng"
            ]
        ))
        
        # Section 4: Translation
        content_layout.addWidget(self._create_section(
            "🌐 Bước 4: Dịch Slide (Tùy chọn)",
            [
                "1. Sau khi tạo xong outline, nhấn '🌐 Dịch slide'",
                "2. Chọn ngôn ngữ đích:",
                "   - 🇻🇳 Việt → 🇺🇸 Anh",
                "   - 🇻🇳 Việt → 🇯🇵 Nhật",
                "   - Hoặc chiều ngược lại",
                "3. Chọn slide cần dịch (hoặc tất cả)",
                "4. Nhấn 'Dịch' → Chờ AI dịch",
                "5. Nhấn 'Xuất file đã dịch' để lưu"
            ]
        ))
        
        # Section 5: Export
        content_layout.addWidget(self._create_section(
            "📥 Bước 5: Xuất PowerPoint",
            [
                "1. Nhấn '📥 Xuất PowerPoint'",
                "2. Chọn nơi lưu file và đặt tên",
                "3. Nhấn 'Save' để xuất file .pptx",
                "4. Mở file bằng PowerPoint để chỉnh sửa thêm"
            ]
        ))
        
        # Tips section
        content_layout.addWidget(self._create_section(
            "💡 Mẹo sử dụng",
            [
                "• Chủ đề càng cụ thể → Nội dung càng chất lượng",
                "• Thêm nhiều API Key để tăng tốc độ và độ ổn định",
                "• Slide đã tạo có thể xóa bằng nút 🗑️",
                "• Ảnh minh họa được tạo tự động bằng AI"
            ]
        ))
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Đóng")
        close_btn.setObjectName("primaryBtn")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_section(self, title: str, items: list) -> QFrame:
        """Create a section with title and bullet points."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #8B5CF6;")
        layout.addWidget(title_label)
        
        # Items
        for item in items:
            item_label = QLabel(item)
            item_label.setStyleSheet("font-size: 13px; color: #CBD5E1; padding-left: 8px;")
            item_label.setWordWrap(True)
            layout.addWidget(item_label)
        
        return frame
