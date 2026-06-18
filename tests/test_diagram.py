from pathlib import Path

import pytest

from src.core.pptx_generator import PPTXGenerator
from src.data.models import Outline, SlideItem, SlideType


def test_diagram_generation_uses_tmp_path(tmp_path: Path):
    """Generate comparison diagram PPTX without opening files in the OS shell."""
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
                            {"text": "Người yêu cầu", "highlight": False},
                        ],
                    },
                    "after": {
                        "title": "Sau Cải Tiến (Phân loại tự động)",
                        "nodes": [
                            {"text": "Công cụ dịch tự động", "highlight": False},
                            {"text": "Cần chính xác cao -> Team dịch", "highlight": False},
                            {"text": "Tham khảo -> Dùng bản dịch máy", "highlight": False},
                            {"text": "Không liên quan -> Bỏ qua", "highlight": False},
                        ],
                    },
                    "benefits": [
                        "Tập trung nguồn lực vào tài liệu quan trọng",
                        "Dịch nhanh VN-JP bằng công cụ hỗ trợ",
                        "Giữ nguyên định dạng PDF/Hình ảnh",
                    ],
                },
            ),
        ],
    )

    output_path = tmp_path / "test_comparison_diagram.pptx"
    PPTXGenerator().generate(outline, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


@pytest.mark.integration
def test_diagram_manual_open_integration(tmp_path: Path):
    """Optional manual OS open check; skipped by default."""
    pytest.skip("Manual os.startfile check is intentionally excluded from default unit tests.")
