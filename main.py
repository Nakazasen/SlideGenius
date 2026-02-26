# Nhập các mô-đun cần thiết
import sys  # Cung cấp quyền truy cập vào các biến và hàm được duy trì bởi trình thông dịch Python
from PySide6.QtWidgets import QApplication  # Lớp chính cho các ứng dụng GUI PySide6
from PySide6.QtGui import QFont  # Để quản lý phông chữ trong ứng dụng
from src.app import SlideGeniusApp  # Nhập lớp ứng dụng chính từ tệp app.py
from src.utils.logger import setup_logging  # Import logger setup


def main():  # Định nghĩa hàm chính, điểm bắt đầu của ứng dụng
    """Main entry point for the application."""  # Docstring giải thích mục đích của hàm
    # Setup Logging first
    setup_logging(debug=True)
    
    # Tạo một đối tượng QApplication, đây là yêu cầu cho bất kỳ ứng dụng PySide6 nào
    app = QApplication(sys.argv)
    
    # Thiết lập siêu dữ liệu cho ứng dụng
    app.setApplicationName("SlideGenius")  # Đặt tên ứng dụng
    app.setApplicationVersion("1.0.0")  # Đặt phiên bản ứng dụng
    app.setOrganizationName("SlideGenius")  # Đặt tên tổ chức
    
    # Thiết lập phông chữ mặc định cho ứng dụng
    font = QFont("Segoe UI", 10)  # Tạo một đối tượng phông chữ với "Segoe UI" kích thước 10
    app.setFont(font)  # Áp dụng phông chữ cho toàn bộ ứng dụng
    
    # Tạo và hiển thị cửa sổ chính của ứng dụng
    window = SlideGeniusApp()  # Tạo một thể hiện của lớp ứng dụng chính
    window.show()  # Hiển thị cửa sổ
    
    # Bắt đầu vòng lặp sự kiện của ứng dụng và thoát khi nó kết thúc
    sys.exit(app.exec())


# Kiểm tra xem tập lệnh này có được chạy trực tiếp hay không
if __name__ == "__main__":
    # Nếu đúng, gọi hàm main() để khởi chạy ứng dụng
    main()