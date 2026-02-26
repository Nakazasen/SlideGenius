# Phase 01: Project Setup

**Status:** ✅ Complete  
**Dependencies:** None  
**Estimated Time:** 30 minutes

---

## 🎯 Objective

Thiết lập môi trường phát triển, cài đặt dependencies, và tạo cấu trúc thư mục cơ bản cho dự án SlideGenius.

---

## ✅ Requirements

### Functional

- [ ] Tạo virtual environment Python
- [ ] Cài đặt tất cả dependencies cần thiết
- [ ] Tạo cấu trúc thư mục theo plan
- [ ] Tạo file entry point (main.py) chạy được

### Non-Functional

- [ ] Python 3.10+ compatibility
- [ ] Cấu trúc code clean, dễ mở rộng

---

## 📋 Implementation Steps

### 1. [ ] Tạo Virtual Environment

```bash
cd c:\ProgramData\Sandbox\SlideGenius
python -m venv venv
.\venv\Scripts\activate
```

### 2. [ ] Tạo requirements.txt

```
# Core
PySide6>=6.6.0
python-pptx>=0.6.21
google-generativeai>=0.3.0

# Database
# (SQLite is built-in)

# Utilities
Pillow>=10.0.0        # Image handling
```

### 3. [ ] Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 4. [ ] Tạo Folder Structure

```
src/
├── __init__.py
├── app.py
├── core/
│   └── __init__.py
├── data/
│   └── __init__.py
├── ui/
│   ├── __init__.py
│   ├── components/
│   │   └── __init__.py
│   ├── dialogs/
│   │   └── __init__.py
│   └── styles/
└── utils/
    └── __init__.py
assets/
├── icons/
├── templates/
└── fonts/
```

### 5. [ ] Tạo main.py (Entry Point)

```python
"""SlideGenius - AI Slide Generator"""
import sys
from PySide6.QtWidgets import QApplication
from src.app import SlideGeniusApp

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SlideGenius")
    app.setApplicationVersion("1.0.0")
    
    window = SlideGeniusApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### 6. [ ] Tạo src/app.py (Basic Window)

```python
"""Main Application Window"""
from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Qt

class SlideGeniusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SlideGenius - AI Slide Generator")
        self.setMinimumSize(1200, 700)
        
        # Placeholder
        label = QLabel("🚀 SlideGenius is running!")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
```

### 7. [ ] Tạo config.json mặc định

```json
{
  "version": "1.0.0",
  "api": {
    "gemini_key": "",
    "model": "gemini-1.5-flash"
  },
  "generation": {
    "creativity_level": 70,
    "auto_generate_images": false,
    "include_speaker_notes": true,
    "default_language": "vi"
  },
  "ui": {
    "theme": "dark",
    "window_width": 1400,
    "window_height": 900
  },
  "paths": {
    "output_folder": "",
    "last_opened": ""
  }
}
```

### 8. [ ] Test chạy ứng dụng

```bash
python main.py
```

→ Phải hiện cửa sổ với text "SlideGenius is running!"

---

## 📁 Files to Create

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `main.py` | Application entry point |
| `src/__init__.py` | Package marker |
| `src/app.py` | Main window class |
| `src/core/__init__.py` | Core package |
| `src/data/__init__.py` | Data package |
| `src/ui/__init__.py` | UI package |
| `src/ui/components/__init__.py` | Components package |
| `src/ui/dialogs/__init__.py` | Dialogs package |
| `src/utils/__init__.py` | Utils package |
| `config.json` | Default configuration |

---

## 🧪 Test Criteria

- [ ] `python main.py` chạy không lỗi
- [ ] Cửa sổ hiện ra với kích thước tối thiểu 1200x700
- [ ] Import PySide6 thành công
- [ ] Import google-generativeai thành công
- [ ] Import python-pptx thành công

---

## 📝 Notes

- Chưa cần theme system ở phase này
- Chưa cần kết nối database
- Focus: Environment chạy được

---

**Next Phase:** [Phase 02 - Core Infrastructure](phase-02-core.md)
