"""Main Application Window for SlideGenius."""
# Nhập các lớp và hàm cần thiết từ thư viện PySide6
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                                QVBoxLayout, QLabel, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt
# Nhập các mô-đun tùy chỉnh từ dự án
from src.ui.theme_manager import ThemeManager # Quản lý giao diện (sáng/tối)
from src.ui.components.sidebar import Sidebar # Thanh bên điều hướng
from src.ui.components.input_panel import InputPanel # Bảng nhập liệu cho người dùng
from src.ui.components.outline_editor import OutlineEditor # Trình chỉnh sửa dàn ý slide
from src.ui.dialogs.settings_dialog import SettingsDialog # Hộp thoại cài đặt
from src.core.ai_service import AIService # Dịch vụ AI để tạo nội dung
from src.data.models import Outline # Mô hình dữ liệu cho dàn ý
from src.ui.screens import HomeScreen, HistoryScreen, TemplatesScreen  # Các màn hình
from src.ui.workers import GenerateWorker # Worker thread
from src.data.templates import TEMPLATE_LIST # Dữ liệu mẫu






class SlideGeniusApp(QMainWindow): # Lớp chính của ứng dụng, kế thừa từ QMainWindow
    """Main application window with 3-column layout.""" # Docstring mô tả lớp
    
    def __init__(self): # Hàm khởi tạo của cửa sổ chính
        super().__init__() # Gọi hàm khởi tạo của lớp cha (QMainWindow)
        self.setWindowTitle("Tạo Slide PowerPoint tự động bằng AI") # Đặt tiêu đề cho cửa sổ
        self.setMinimumSize(1200, 700) # Đặt kích thước tối thiểu cho cửa sổ
        self.resize(1400, 900) # Thay đổi kích thước cửa sổ thành kích thước mặc định
        
        # Khởi tạo các dịch vụ
        self.theme_manager = ThemeManager() # Tạo đối tượng quản lý giao diện
        self.ai_service = AIService() # Tạo đối tượng dịch vụ AI
        self.worker = None # Khởi tạo worker là None ban đầu
        
        # Thiết lập giao diện người dùng
        self._setup_ui() # Gọi phương thức để thiết lập UI
        
        # Áp dụng giao diện
        self.theme_manager.apply_theme() # Áp dụng giao diện (sáng/tối) hiện tại
        self._update_theme_button() # Cập nhật văn bản của nút chuyển đổi giao diện
    
    def _setup_ui(self): # Phương thức để thiết lập bố cục giao diện chính
        """Setup the main UI layout.""" # Docstring mô tả phương thức
        central = QWidget() # Tạo một widget trung tâm
        self.setCentralWidget(central) # Đặt nó làm widget trung tâm của cửa sổ chính
        
        main_layout = QHBoxLayout(central) # Tạo một bố cục ngang chính cho widget trung tâm
        main_layout.setContentsMargins(0, 0, 0, 0) # Xóa lề của bố cục
        main_layout.setSpacing(0) # Xóa khoảng cách giữa các widget con
        
        # === CỘT TRÁI: Thanh bên ===
        self.sidebar = Sidebar() # Tạo một widget thanh bên
        self.sidebar.navigation_changed.connect(self._on_navigation) # Kết nối tín hiệu điều hướng với phương thức xử lý
        main_layout.addWidget(self.sidebar) # Thêm thanh bên vào bố cục chính
        
        # === CỘT GIỮA: Khu vực nội dung với QStackedWidget ===
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentArea")
        
        # Tạo các màn hình
        self.home_screen = HomeScreen()
        self.home_screen.generate_clicked.connect(self._on_generate)
        self.home_screen.express_clicked.connect(self._on_express_generate)
        self.home_screen.export_clicked.connect(self._on_export)
        self.home_screen.translate_clicked.connect(self._on_translate)
        
        self.history_screen = HistoryScreen()
        self.history_screen.outline_selected.connect(self._on_history_selected)
        
        self.templates_screen = TemplatesScreen()
        self.templates_screen.template_selected.connect(self._on_template_from_screen)
        
        # Thêm vào stack (index: 0=home, 1=history, 2=templates)
        self.content_stack.addWidget(self.home_screen)
        self.content_stack.addWidget(self.history_screen)
        self.content_stack.addWidget(self.templates_screen)
        
        # Aliases cho backward compatibility
        self.input_panel = self.home_screen.input_panel
        self.outline_editor = self.home_screen.outline_editor
        
        main_layout.addWidget(self.content_stack, 1)
        
        # === CỘT PHẢI: Bảng điều khiển ===
        self.right_panel = QWidget() # Tạo widget cho bảng điều khiển bên phải
        self.right_panel.setObjectName("rightPanel") # Đặt tên đối tượng để tạo kiểu
        self.right_panel.setFixedWidth(320) # Đặt chiều rộng cố định
        right_layout = QVBoxLayout(self.right_panel) # Tạo bố cục dọc
        right_layout.setContentsMargins(20, 20, 20, 20) # Đặt lề
        right_layout.setSpacing(16) # Đặt khoảng cách
        
        panel_title = QLabel("🎨 Thư viện Mẫu") # Tạo nhãn tiêu đề cho bảng
        panel_title.setObjectName("panelTitle") # Đặt tên đối tượng để tạo kiểu
        right_layout.addWidget(panel_title) # Thêm tiêu đề vào bố cục
        
        # Các nút mẫu với logic chọn
        self.templates = TEMPLATE_LIST
        
        self.template_buttons = {}  # Lưu reference đến các nút
        self.selected_template = "executive_blue"  # Mẫu mặc định
        
        for template_id, name, color, desc in self.templates:
            btn = self._create_template_btn(template_id, name, color, desc)
            self.template_buttons[template_id] = btn
            right_layout.addWidget(btn)
        
        # Đánh dấu mẫu mặc định là đã chọn
        self._update_template_selection("executive_blue")
        
        right_layout.addStretch() # Thêm một không gian co giãn để đẩy các nút lên trên
        
        main_layout.addWidget(self.right_panel) # Thêm bảng điều khiển bên phải vào bố cục chính
        
        # Thanh trạng thái
        self.statusBar().showMessage("Sẵn sàng") # Hiển thị thông báo "Ready" trên thanh trạng thái
    
    def _create_template_btn(self, template_id: str, name: str, color: str, desc: str = "") -> QWidget:
        """Create a template button with selection support."""
        from PySide6.QtWidgets import QPushButton
        btn = QPushButton(f"  {name}")
        btn.setCheckable(True)  # Cho phép bật/tắt nút
        btn.setProperty("template_id", template_id)
        btn.setProperty("template_color", color)
        btn.setToolTip(desc)  # Thêm mô tả khi hover
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
            QPushButton:hover {{
                background-color: {color}11;
            }}
            QPushButton:checked {{
                background-color: {color}22;
                border-left: 4px solid {color};
                font-weight: bold;
            }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda checked, tid=template_id, n=name: self._on_template_selected(tid, n))
        return btn
    
    def _on_template_selected(self, template_id: str, name: str):
        """Handle template selection."""
        self._update_template_selection(template_id)
        self.statusBar().showMessage(f"✅ Đã chọn mẫu: {name}")
        
        # Lưu vào config
        from src.data.config_manager import ConfigManager
        config = ConfigManager()
        config.set("template.selected", template_id)
    
    def _update_template_selection(self, selected_id: str):
        """Update visual state of template buttons."""
        self.selected_template = selected_id
        for tid, btn in self.template_buttons.items():
            btn.setChecked(tid == selected_id)
    
    def _on_navigation(self, key: str): # Phương thức xử lý các sự kiện điều hướng từ thanh bên
        """Handle navigation events."""
        if key == "toggle_theme":
            self.theme_manager.toggle_theme()
            self._update_theme_button()
        elif key == "settings":
            self._show_settings()
        elif key == "help":
            self._show_help()
        elif key == "home":
            self.content_stack.setCurrentIndex(0)  # HomeScreen
            self.right_panel.show()
            self.statusBar().showMessage("🏠 Trang chủ - Tạo Slide mới")
        elif key == "history":
            self.content_stack.setCurrentIndex(1)  # HistoryScreen
            self.right_panel.hide()
            self.statusBar().showMessage("📜 Lịch sử tạo slide")
        elif key == "templates":
            self.content_stack.setCurrentIndex(2)  # TemplatesScreen
            self.right_panel.hide()
            self.statusBar().showMessage("🎨 Thư viện Mẫu Slide")
    
    def _update_theme_button(self): # Phương thức cập nhật văn bản của nút giao diện
        """Update theme button text.""" # Docstring mô tả
        # Gọi phương thức trên thanh bên để cập nhật nút, truyền vào trạng thái có phải là giao diện tối hay không
        self.sidebar.update_theme_button(self.theme_manager.is_dark())
    
    def _show_settings(self): # Phương thức hiển thị hộp thoại cài đặt
        """Show settings dialog.""" # Docstring mô tả
        dialog = SettingsDialog(self) # Tạo một thể hiện của hộp thoại cài đặt
        if dialog.exec(): # Hiển thị hộp thoại và chờ người dùng đóng nó (nhấp OK hoặc Cancel)
            # Nếu người dùng nhấp OK (dialog.exec() trả về True)
            self.ai_service.reconfigure() # Cấu hình lại dịch vụ AI với các cài đặt mới
            self.statusBar().showMessage("Đã lưu cài đặt") # Hiển thị thông báo đã lưu
    
    def _show_help(self):
        """Show help dialog."""
        from src.ui.dialogs.help_dialog import HelpDialog
        dialog = HelpDialog(self)
        dialog.exec()
    
    def _on_history_selected(self, data: dict):
        """Handle selection from history screen."""
        import json
        try:
            outline_json = data.get('outline_json', '{}')
            outline_data = json.loads(outline_json) if isinstance(outline_json, str) else outline_json
            outline = Outline.from_dict(outline_data)
            self.outline_editor.set_outline(outline)
            # Switch to home screen to show the outline
            self.content_stack.setCurrentIndex(0)
            self.right_panel.show()
            self.statusBar().showMessage(f"📂 Đã mở: {data.get('title', 'Untitled')}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể mở outline: {str(e)}")
    
    def _on_template_from_screen(self, template_id: str, name: str):
        """Handle template selection from templates screen."""
        self._update_template_selection(template_id)
        self.statusBar().showMessage(f"✅ Đã chọn mẫu: {name}")
    
    def _on_generate(self, prompt: str, num_slides: int): # Phương thức xử lý yêu cầu tạo dàn ý
        """Handle generate request.""" # Docstring mô tả
        if not self.ai_service.is_configured(): # Kiểm tra xem khóa API đã được cấu hình chưa
            QMessageBox.warning( # Nếu chưa, hiển thị một hộp thoại cảnh báo
                self, "Yêu cầu API Key",
                "Vui lòng vào Settings để nhập Gemini API key."
            )
            self._show_settings() # Mở hộp thoại cài đặt để người dùng nhập khóa
            return # Dừng thực thi
            
        # Hiển thị Wizard tùy chỉnh
        from src.ui.dialogs.wizard_dialog import WizardDialog
        wizard = WizardDialog(self)
        if not wizard.exec():
            return  # User Cancelled
            
        context = wizard.get_data()
        
        # Save wizard preferences for next time
        from src.data.config_manager import ConfigManager
        config = ConfigManager()
        config.set("wizard_preferences.audience_index", wizard.audience_combo.currentIndex())
        config.set("wizard_preferences.tone_index", wizard.tone_combo.currentIndex())
        config.set("wizard_preferences.style_id", wizard.style_bg.checkedId())
        
        # Bắt đầu quá trình tạo trong nền
        self.input_panel.set_loading(True) # Hiển thị chỉ báo tải trên bảng nhập liệu
        self.statusBar().showMessage(f"Đang tạo outline cho {context.get('audience')}...")
        
        # Tạo và khởi động worker
        self.worker = GenerateWorker(self.ai_service, prompt, num_slides, context) # Tạo một worker mới
        self.worker.progress.connect(lambda msg: self.input_panel.set_loading(True, msg))
        self.worker.finished.connect(self._on_generate_finished) # Kết nối tín hiệu hoàn thành
        self.worker.error.connect(self._on_generate_error) # Kết nối tín hiệu lỗi
        self.worker.start() # Bắt đầu luồng worker

    def _on_express_generate(self, prompt: str, num_slides: int, template_id: str):
        """Handle express generate request."""
        # 1. Update template selection
        self._on_template_selected(template_id, "") # name param optional here
        
        # 2. Proceed with normal generation
        # The stored self.selected_template will be used during export
        self._on_generate(prompt, num_slides)
    
    def _on_generate_finished(self, outline: Outline): # Phương thức xử lý khi việc tạo hoàn tất
        """Handle generation complete.""" # Docstring mô tả
        self.input_panel.set_loading(False) # Ẩn chỉ báo tải
        
        if outline: # Nếu dàn ý được tạo thành công
            self.outline_editor.set_outline(outline) # Đặt dàn ý cho trình chỉnh sửa
            self.statusBar().showMessage(f"✅ Đã tạo {outline.slide_count} slides") # Hiển thị thông báo thành công
        else: # Nếu không thể tạo dàn ý
            self.statusBar().showMessage("❌ Không thể tạo outline") # Hiển thị thông báo lỗi
            QMessageBox.warning(self, "Error", "Không thể tạo outline. Vui lòng thử lại.") # Hiển thị hộp thoại lỗi
    
    def _on_generate_error(self, error: str): # Phương thức xử lý khi có lỗi xảy ra trong quá trình tạo
        """Handle generation error.""" # Docstring mô tả
        self.input_panel.set_loading(False) # Ẩn chỉ báo tải
        self.statusBar().showMessage(f"❌ Error: {error}") # Hiển thị thông báo lỗi chi tiết
        QMessageBox.critical(self, "Error", f"Lỗi: {error}") # Hiển thị hộp thoại lỗi nghiêm trọng
    
    def _on_translate(self):
        """Handle translate request - open translation dialog."""
        outline = self.outline_editor.get_outline()
        if not outline:
            QMessageBox.warning(self, "Lỗi", "Chưa có dàn ý để dịch!")
            return
        
        from src.ui.dialogs.translation_dialog import TranslationDialog
        dialog = TranslationDialog(outline, self)
        dialog.exec()
    
    def _on_export(self): # Phương thức xử lý yêu cầu xuất ra file PowerPoint
        """Handle export request.""" # Docstring mô
        # Nhập các mô-đun cần thiết cục bộ để tránh nhập vòng tròn và chỉ nhập khi cần
        from pathlib import Path
        from PySide6.QtWidgets import QFileDialog
        from src.core.pptx_generator import PPTXGenerator, TEMPLATES
        from src.ui.dialogs.success_dialog import SuccessDialog
        from src.data.database import DatabaseManager
        
        outline = self.outline_editor.get_outline() # Lấy dàn ý hiện tại từ trình chỉnh sửa
        if not outline: # Nếu không có dàn ý
            return # Dừng thực thi
        
        # Lấy vị trí lưu file (Sanitize filename)
        import re
        safe_title = re.sub(r'[\\/*?:"<>|]', "", outline.title)  # Remove unsafe chars
        safe_title = re.sub(r'\s+', "_", safe_title)  # Replace spaces with underscores
        safe_title = safe_title[:50]  # Truncate to 50 chars
        safe_title = safe_title.strip("_")  # Remove leading/trailing underscores
        
        default_name = f"{safe_title}.pptx"
        file_path, _ = QFileDialog.getSaveFileName( # Mở hộp thoại "Lưu file"
            self, "Lưu PowerPoint",
            default_name,
            "PowerPoint Files (*.pptx)"
        )
        
        if not file_path: # Nếu người dùng không chọn file (nhấp Cancel)
            return # Dừng thực thi
        
        try: # Bắt đầu khối try-except để xử lý lỗi xuất file
            self.statusBar().showMessage("Đang xuất PowerPoint...") # Hiển thị thông báo đang xuất
            
            # Tạo file PPTX
            selected_tmpl_config = TEMPLATES.get(self.selected_template)
            if not selected_tmpl_config:
                # Fallback if somehow invalid
                selected_tmpl_config = TEMPLATES.get("executive_blue")
                
            generator = PPTXGenerator(selected_tmpl_config) # Tạo một trình tạo PPTX với một mẫu cụ thể
            output_path = generator.generate(outline, Path(file_path)) # Gọi phương thức tạo và lấy đường dẫn file đầu ra
            
            # Lưu vào lịch sử
            db = DatabaseManager() # Tạo đối tượng quản lý cơ sở dữ liệu
            db.add_history( # Thêm một bản ghi vào lịch sử
                title=outline.title,
                prompt=self.input_panel.get_prompt(),
                outline_json=outline.to_json(),
                template_name=self.selected_template,
                output_path=str(output_path),
                slide_count=outline.slide_count
            )
            
            self.statusBar().showMessage(f"✅ Đã xuất {outline.slide_count} slides") # Hiển thị thông báo xuất thành công
            
            # Hiển thị hộp thoại thành công
            dialog = SuccessDialog(output_path, outline.slide_count, self) # Tạo hộp thoại
            dialog.exec() # Hiển thị hộp thoại
            
        except Exception as e: # Nếu có lỗi xảy ra trong quá trình xuất
            self.statusBar().showMessage(f"❌ Lỗi export: {e}") # Hiển thị thông báo lỗi
            QMessageBox.critical(self, "Export Error", f"Không thể xuất file: {e}") # Hiển thị hộp thoại lỗi nghiêm trọng
