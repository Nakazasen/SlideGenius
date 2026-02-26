import sys
import os
# Add project root
sys.path.append(os.getcwd())

from pathlib import Path
from src.data.models import Outline, SlideItem, SlideType
from src.core.pptx_generator import PPTXGenerator

def test_diagram_generation():
    print("Testing Smart Diagram Generation (Comparison)...")
    
    # Create a mock Outline with a Comparison Diagram Slide
    outline = Outline(
        title="Cải Tiến Quy Trình Dịch Thuật",
        slides=[
            SlideItem(title="Cải Tiến Quy Trình Dịch Thuật", slide_type=SlideType.TITLE),
            SlideItem(
                title="Quy Trình Dịch Tài Liệu",
                slide_type=SlideType.DIAGRAM,
                speaker_notes="Sơ đồ thể hiện sự khác biệt giữa quy trình trước và sau cải tiến.",
                diagram={
                    "type": "comparison",
                    "before": {
                        "title": "Trước Cải Tiến",
                        "nodes": [
                            {"text": "Nguồn tài liệu (JP, CN...)", "highlight": False},
                            {"text": "Team Phiên Dịch (Quá tải)", "highlight": True},
                            {"text": "Người yêu cầu", "highlight": False}
                        ]
                    },
                    "after": {
                        "title": "Sau Cải Tiến (Phân loại tự động)",
                        "nodes": [
                            {"text": "Công cụ dịch tự động", "highlight": False},
                            {"text": "Cần chính xác cao -> Team dịch", "highlight": False},
                            {"text": "Tham khảo -> Dùng bản dịch máy", "highlight": False},
                            {"text": "Không liên quan -> Bỏ qua", "highlight": False}
                        ]
                    },
                    "benefits": [
                        "Tập trung nguồn lực vào tài liệu quan trọng",
                        "Dịch nhanh VN-JP bằng công cụ hỗ trợ",
                        "Giữ nguyên định dạng PDF/Hình ảnh"
                    ]
                }
            )
        ]
    )
    
    # Generate PPTX
    generator = PPTXGenerator()
    output_path = Path("test_comparison_diagram.pptx")
    generator.generate(outline, output_path)
    
    print(f"Generated: {output_path.absolute()}")
    import os
    os.startfile(output_path)

if __name__ == "__main__":
    test_diagram_generation()
