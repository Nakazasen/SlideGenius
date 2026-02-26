# ⚡ SlideGenius - AI Slide Generator

<p align="center">
  <strong>Tạo slide PowerPoint đẹp chỉ trong vài giây với sức mạnh AI</strong>
</p>

---

## 🎯 Giới thiệu

**SlideGenius** là ứng dụng Desktop Windows giúp tạo bài thuyết trình PowerPoint nhanh chóng bằng AI. Chỉ cần nhập ý tưởng → AI tạo outline → Xuất file PPTX!

### ✨ Tính năng chính

- 🤖 **AI Generation**: Sử dụng Google Gemini để tạo nội dung thông minh
- 📝 **Smart Outliner**: Xem và chỉnh sửa outline trước khi xuất
- 🎨 **5 Templates**: Modern Blue, Creative Orange, Minimal Gray, Nature Green, Purple Gradient
- 📥 **Native PPTX Export**: Xuất file PowerPoint thật, chỉnh sửa được
- 🌙 **Dark/Light Mode**: Giao diện tối/sáng tùy chọn
- 📋 **History**: Lưu lịch sử các slide đã tạo

---

## 🚀 Cài đặt

### Yêu cầu

- Python 3.10+
- Windows 10/11
- Gemini API Key (miễn phí từ Google AI Studio)

### Bước 1: Clone/Download

```bash
cd c:\ProgramData\Sandbox\SlideGenius
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Lấy API Key

1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Tạo API key mới (miễn phí!)
3. Copy key để dùng trong app

### Bước 4: Chạy ứng dụng

```bash
python main.py
```

---

## 📖 Hướng dẫn sử dụng

### 1. Cấu hình API Key

- Click **⚙️ Settings** trong sidebar
- Paste API key vào ô "Gemini API Key"
- Click **Test Connection** để kiểm tra
- Click **Save**

### 2. Tạo Slide

1. Nhập ý tưởng vào ô prompt, ví dụ:
   - "Báo cáo doanh thu quý 4 năm 2025"
   - "Giới thiệu sản phẩm mới cho team marketing"
   - "Bài thuyết trình về AI trong doanh nghiệp"

2. Chọn số slides (3-20)

3. Click **🚀 Tạo Outline**

4. Xem và chỉnh sửa outline (xóa slide nếu cần)

5. Click **📥 Xuất PowerPoint**

6. Chọn nơi lưu file

7. Mở file trong PowerPoint để chỉnh sửa thêm!

---

## 🎨 Templates

| Template | Màu chủ đạo | Phù hợp cho |
|----------|-------------|-------------|
| Modern Blue | 🔵 Xanh dương | Doanh nghiệp, Chuyên nghiệp |
| Creative Orange | 🟠 Cam | Sáng tạo, Marketing |
| Minimal Gray | ⚫ Xám | Tối giản, Học thuật |
| Nature Green | 🟢 Xanh lá | Giáo dục, Môi trường |
| Purple Gradient | 🟣 Tím | Công nghệ, Startup |

---

## 🛠️ Tech Stack

- **UI**: PySide6 (Qt 6)
- **AI**: Google Generative AI (Gemini)
- **PPTX**: python-pptx
- **Database**: SQLite
- **Styling**: QSS (Qt Style Sheets)

---

## 📁 Cấu trúc Project

```
SlideGenius/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config.json            # User settings
├── slidegenius.db         # History database
│
├── src/
│   ├── app.py             # Main window
│   ├── core/              # Business logic
│   │   ├── ai_service.py
│   │   └── pptx_generator.py
│   ├── data/              # Data layer
│   │   ├── config_manager.py
│   │   ├── database.py
│   │   └── models.py
│   └── ui/                # User interface
│       ├── theme_manager.py
│       ├── components/
│       ├── dialogs/
│       └── styles/
│
├── assets/                 # Static files
├── docs/                   # Documentation
└── plans/                  # Development plans
```

---

## 🔮 Roadmap

### Phase 2 (Coming Soon)

- 📎 Upload PDF/Word để tạo slide
- 🔗 Dán link website để tạo slide
- 🌐 Dịch slide sang Anh/Nhật/Hàn/Trung
- 🖼️ AI tự động tạo hình ảnh

---

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

---

## 🙏 Credits

- Built with ❤️ using PySide6 + Google Gemini
- Icons: Emoji (built-in)

---

<p align="center">
  <strong>Made with ⚡ by SlideGenius Team</strong>
</p>
