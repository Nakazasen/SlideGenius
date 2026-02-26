# 📋 Plan: SlideGenius - AI Slide Generator

**Created:** 2026-01-20 06:19  
**Status:** 🟡 In Progress  
**Complexity:** Medium (Desktop App MVP)

---

## 📖 Overview

SlideGenius là ứng dụng Desktop Windows giúp tạo slide PowerPoint nhanh chóng bằng AI. User nhập prompt hoặc ý tưởng → AI tạo outline → User chỉnh sửa → Xuất file PPTX.

### Target MVP Features

1. ✅ AI Chatbox - Nhập prompt tạo outline
2. ✅ Smart Outliner - Chỉnh sửa outline trước khi tạo
3. ✅ Native PPTX Export - Xuất file PowerPoint
4. ✅ Template Library - 5 mẫu template
5. ✅ Settings - Cài đặt API Key
6. ✅ History - Lưu lịch sử local (SQLite)
7. ✅ Light/Dark Theme - Đổi giao diện

---

## 🛠️ Tech Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| **UI Framework** | PySide6 (Qt 6) | Modern, native look, rich widgets |
| **AI Engine** | Google Generative AI (Gemini) | Free tier, fast, structured output |
| **PPTX Generator** | python-pptx | Standard, stable, feature-rich |
| **Database** | SQLite | Local, no setup, lightweight |
| **Config** | JSON file | Simple, human-readable |
| **Styling** | QSS (Qt Style Sheets) | CSS-like, theme support |

---

## 📊 Phases Overview

| Phase | Name | Tasks | Status | Progress |
|-------|------|-------|--------|----------|
| 01 | Project Setup | 8 | ✅ Complete | 100% |
| 02 | Core Infrastructure | 12 | ✅ Complete | 100% |
| 03 | Main UI Shell | 10 | ✅ Complete | 100% |
| 04 | AI & Outline Features | 14 | ✅ Complete | 100% |
| 05 | PPTX Generation | 10 | ✅ Complete | 100% |
| 06 | Polish & Testing | 8 | ✅ Complete | 100% |

**Tổng:** 62 tasks | **Ước tính:** 4-6 coding sessions

---

## 📁 Project Structure (Target)

```
SlideGenius/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── config.json               # User settings (API key, theme)
├── slidegenius.db            # SQLite database (history)
│
├── src/
│   ├── __init__.py
│   ├── app.py                # QApplication setup
│   │
│   ├── core/                 # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py     # Gemini API integration
│   │   ├── pptx_generator.py # PowerPoint generation
│   │   ├── outline_model.py  # Outline data structure
│   │   └── template_engine.py # Template management
│   │
│   ├── data/                 # Data layer
│   │   ├── __init__.py
│   │   ├── config_manager.py # JSON config read/write
│   │   ├── database.py       # SQLite operations
│   │   └── models.py         # Data models (Slide, Template, History)
│   │
│   ├── ui/                   # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main application window
│   │   ├── theme_manager.py  # Light/Dark theme switching
│   │   │
│   │   ├── components/       # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── sidebar.py
│   │   │   ├── input_panel.py
│   │   │   ├── outline_editor.py
│   │   │   └── template_picker.py
│   │   │
│   │   ├── dialogs/          # Modal dialogs
│   │   │   ├── __init__.py
│   │   │   ├── settings_dialog.py
│   │   │   └── success_dialog.py
│   │   │
│   │   └── styles/           # QSS stylesheets
│   │       ├── light.qss
│   │       └── dark.qss
│   │
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── constants.py      # App constants
│       └── helpers.py        # Helper functions
│
├── assets/                   # Static assets
│   ├── icons/                # App icons
│   ├── templates/            # PPTX template files
│   └── fonts/                # Custom fonts (Inter)
│
├── docs/                     # Documentation
│   ├── BRIEF.md
│   └── design-specs.md
│
└── plans/                    # This folder
    ├── plan.md
    └── phase-*.md
```

---

## 🗄️ Database Schema

### Table: `history`

```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    prompt TEXT,
    outline_json TEXT,          -- JSON string of outline
    template_name TEXT,
    output_path TEXT,           -- Path to generated PPTX
    slide_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table: `templates`

```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT,
    description TEXT,
    category TEXT,              -- Business, Education, Creative, Minimal
    preview_path TEXT,          -- Path to preview image
    config_json TEXT,           -- Template configuration (colors, fonts)
    is_builtin BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙️ Config Schema (config.json)

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

---

## 🚀 Quick Commands

| Action | Command |
|--------|---------|
| Start Phase 1 | `/code phase-01` |
| Check progress | `/next` |
| View phase details | Open `phase-XX-*.md` |
| Save context | `/save-brain` |

---

## 📝 Notes

- **Priority:** Get basic flow working first (Prompt → Outline → PPTX)
- **Defer:** Image generation, multi-language, file upload (Phase 2 features)
- **Testing:** Manual testing sufficient for MVP
