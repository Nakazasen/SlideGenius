"""AI Service - Gemini API Integration."""
import json
from typing import Optional, Tuple
try:
    # FORCE DISABLE: google.genai hangs on import
    raise ImportError("Disabled due to hang")
    from google import genai
    from google.genai import types
except ImportError:
    import google.generativeai as genai
    types = None
from src.data.config_manager import ConfigManager
from src.data.models import Outline
from src.core.model_cascade import ModelCascade
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AIService:
    """Service to interact with Google Gemini API for content generation."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.cascade = ModelCascade()
        self._configure_api()
    
    def _configure_api(self) -> None:
        """Configure Gemini API with keys from config."""
        api_keys = self.config.get("api.gemini_keys", [])
        # Fallback to single key if list empty (though ConfigManager should migrate)
        if not api_keys:
            single = self.config.get("api.gemini_key", "")
            if single:
                api_keys = [single]
                
        self.cascade.configure_api(api_keys)
    
    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        return bool(self.config.get("api.gemini_keys") or self.config.get("api.gemini_key"))
    
    def reconfigure(self) -> None:
        """Reconfigure API (call after API key change)."""
        self._configure_api()
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection using Waterfall Strategy. Returns (success, message)."""
        if not self.is_configured():
            return False, "API key chưa được cấu hình"
        
        try:
            # We use the cascade to test. If ANY model works, we are good.
            response = self.cascade.generate_content("Say 'OK' if you can hear me.")
            if response.text:
                return True, "Kết nối thành công! ✓ (Waterfall OK)"
            return False, "Không nhận được phản hồi từ bất kỳ model nào"
        except Exception as e:
            return False, f"Lỗi kết nối: {str(e)}"
    
    def generate_outline(self, prompt: str, num_slides: int = 8, context: dict = None) -> Optional[Outline]:
        """Generate presentation outline from prompt.
        
        Args:
            prompt: User's prompt describing the presentation
            num_slides: Target number of slides (3-20)
            context: Dictionary containing customization preferences (audience, tone, style)
            
        Returns:
            Outline object or None if generation fails
        """
        if not self.is_configured():
            raise ValueError("API key chưa được cấu hình. Vui lòng vào Settings để nhập.")
        
        # Clamp slide count
        num_slides = max(1, min(20, num_slides))
        
        # Determine structure guidance based on slide count
        if num_slides <= 2:
            structure_hint = f"""
Cấu trúc bài thuyết trình ({num_slides} slides):
- Chỉ tạo ĐÚNG {num_slides} slide nội dung chính.
- KHÔNG tạo slide Agenda hay Closing riêng lẻ nếu không được yêu cầu.
- Tập trung thẳng vào nội dung người dùng yêu cầu."""
        else:
            structure_hint = """
Cấu trúc bài thuyết trình:
- Slide 1: Title (Mở đầu ấn tượng)
- Slide 2: Agenda / Mục lục
- Các Slide giữa: Nội dung chi tiết hoặc SƠ ĐỒ
- Slide cuối: Closing (Tổng kết & Kêu gọi hành động)"""

        # Customization Context
        context_prompt = ""
        if context:
            context_prompt = f"""
YÊU CẦU TÙY CHỈNH (Ưu tiên hàng đầu):
1. ĐỐI TƯỢNG: {context.get('audience', 'Chung')} -> Điều chỉnh ngôn ngữ/độ khó phù hợp.
2. TONE: {context.get('tone', 'Chuyên nghiệp')}
3. STYLE: {context.get('style', 'Cân bằng')}
   - Nếu "Visual Heavy": Giảm chữ, tập trung vào `image_prompt`.
   - Nếu "Text Heavy": Viết chi tiết, tăng cường số liệu."""

        system_prompt = f'''Bạn là chuyên gia tạo slide thuyết trình chuyên nghiệp, sâu sắc và chi tiết.
Nhiệm vụ: Tạo nội dung bài thuyết trình HOÀN CHỈNH với ĐÚNG {num_slides} slides.

Yêu cầu QUAN TRỌNG về NỘI DUNG:
1.  **Số lượng:** Chỉ tạo chính xác {num_slides} slides.
2.  **Chuyên sâu:** Viết nội dung đầy đủ, phân tích sâu.
3.  **Speaker Notes:** Viết lời bình chi tiết.
4.  **SƠ ĐỒ:** Dùng `slide_type="diagram"` khi cần so sánh/quy trình.
5.  **HÌNH ẢNH:** Thêm `image_prompt`.

{structure_hint}

{context_prompt}

Trả về JSON theo format (KHÔNG có markdown code block):
{{
    "title": "Tiêu đề bài thuyết trình",
    "language": "vi",
    "slides": [
        {{
            "title": "Tiêu đề slide",
            "content": ["Ý 1...", "Ý 2..."],
            "slide_type": "content",
            "speaker_notes": "...",
        }}
    ]
}}

QUY TẮC MÔ TẢ ẢNH (image_prompt):
- Viết bằng TIẾNG ANH.
- Ngắn gọn (dưới 20 từ), tập trung vào chủ thể và bối cảnh.
- Ví dụ: "Professional business meeting in modern office", "A futuristic city skyline with digital data overlays".

CÁC LOẠI SƠ ĐỒ (diagram.type): "process", "comparison", "hierarchy".'''

        try:
            creativity = self.config.get("generation.creativity_level", 70) / 100
            
            # Use ModelCascade instead of direct model call
            if types:
                generation_config = types.GenerateContentConfig(
                    temperature=creativity,
                    response_mime_type="application/json"
                )
            else:
                # Old SDK or fallback
                generation_config = {
                    "temperature": creativity,
                    "response_mime_type": "application/json"
                }

            response = self.cascade.generate_content(
                f"{system_prompt}\n\nYêu cầu của người dùng: {prompt}",
                generation_config=generation_config
            )
            
            # Parse JSON response
            data = json.loads(response.text)
            logger.info(f"Generated outline successfully: {data.get('title', 'Unknown Title')}")
            return Outline.from_dict(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Error: {e}")
            logger.debug(f"Failed Response Text: {response.text}")
            return None
        except Exception as e:
            logger.error(f"AI Error via Cascade: {e}")
            return None
