# 💡 BRIEF: AI Image Generator Integration

**Ngày tạo:** 2026-01-20
**Brainstorm cùng:** User (SlideGenius Owner)

---

## 1. VẤN ĐỀ

- Slide hiện tại chủ yếu là text và hình vẽ cơ bản (Smart Diagrams).
- Thiếu hình ảnh minh họa sống động, background độc đáo, hoặc visual metaphors (ẩn dụ hình ảnh).
- User có danh sách 16 models nhưng chưa tận dụng được model sinh ảnh.

## 2. PHÂN TÍCH MODELS HIỆN CÓ

User đang có cấu hình 16+ models trong `ModelCascade.py`. Trong đó:

### 🌟 Model Sinh Ảnh (Image Generation)

- **`imagen-4.0-ultra-generate-001`**: Đây là model chuyên dụng để tạo ảnh chất lượng cao (Photorealistic, Art, Vector...).
- **`veo-3.1-generate-preview`**: Model chuyên tạo Video (có thể dùng tạo ảnh động/GIF cho slide).

### 🤖 Model Text/Code (Không sinh ảnh trực tiếp)

- `gemini-3-pro/flash`, `gemma-3-*`: Chuyên xử lý text, logic, coding.

## 3. GIẢI PHÁP ĐỀ XUẤT (IDEAS)

### Idea A: "AI Background Designer" 🎨

- **Tính năng:** Tạo hình nền slide độc bản theo chủ đề.
- **Ví dụ:** "Tạo background chủ đề công nghệ tương lai, màu xanh dương, tối giản."
- **Model:** `imagen-4.0-ultra`

### Idea B: "Slide Illustrator" 🖼️

- **Tính năng:** Tự động tạo ảnh minh họa cho nội dung slide.
- **Ví dụ:** Slide nói về "Tăng trưởng", AI tự tạo ảnh "Cây non đang mọc trên các thỏi vàng".
- **Logic:** Gemini (Text) phân tích nội dung -> Viết prompt cho Imagen -> Imagen tạo ảnh -> Chèn vào slide.

### Idea C: "Icon & Mascot Generator" 🧸

- **Tính năng:** Tạo bộ icon hoặc nhân vật đại diện (Mascot) xuyên suốt bài thuyết trình.
- **Ví dụ:** "Tạo robot cute hướng dẫn từng slide."

## 4. TÍNH KHẢ THI (Technical Check)

- **Support:** SlideGenius đang dùng `google-generativeai`. Cần check xem library này có support gọi `imagen` model không (thường là có, nhưng endpoint khác text).
- **Code:** Cần viết thêm class `ImageGenerator` tương tự `PPTXGenerator` nhưng chuyên xử lý ảnh.

## 5. BƯỚC TIẾP THEO

User chọn Idea nào để triển khai? (Thường là kết hợp A & B).
