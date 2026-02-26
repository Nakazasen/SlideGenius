# Phase 02: Core Infrastructure

**Status:** ✅ Complete  
**Dependencies:** Phase 01 (Setup)  
**Estimated Time:** 1-2 hours

---

## 🎯 Objective

Xây dựng các service cốt lõi: Config Manager, Database, AI Service. Đây là "backbone" của ứng dụng.

---

## ✅ Requirements

### Functional

- [ ] Config Manager đọc/ghi config.json
- [ ] Database Manager tạo tables và CRUD operations
- [ ] AI Service kết nối Gemini API và generate outline
- [ ] Outline Model xử lý cấu trúc dữ liệu slide

### Non-Functional

- [ ] Error handling cho API calls
- [ ] Logging cho debug
- [ ] Type hints đầy đủ

---

## 📋 Implementation Steps

### 1. [ ] Tạo Constants (src/utils/constants.py)

```python
"""Application Constants"""
from pathlib import Path

# Paths
APP_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = APP_DIR / "config.json"
DATABASE_FILE = APP_DIR / "slidegenius.db"
ASSETS_DIR = APP_DIR / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"

# App Info
APP_NAME = "SlideGenius"
APP_VERSION = "1.0.0"

# AI
DEFAULT_MODEL = "gemini-1.5-flash"
MAX_SLIDES = 20
MIN_SLIDES = 3

# UI
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700
```

### 2. [ ] Tạo Config Manager (src/data/config_manager.py)

```python
"""Configuration Manager - Read/Write JSON config"""
import json
from pathlib import Path
from typing import Any, Optional
from src.utils.constants import CONFIG_FILE

class ConfigManager:
    _instance = None
    _config: dict = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self) -> None:
        """Load config from file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = self._default_config()
            self._save()
    
    def _save(self) -> None:
        """Save config to file"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def _default_config(self) -> dict:
        """Return default configuration"""
        return {
            "version": "1.0.0",
            "api": {"gemini_key": "", "model": "gemini-1.5-flash"},
            "generation": {
                "creativity_level": 70,
                "auto_generate_images": False,
                "include_speaker_notes": True,
                "default_language": "vi"
            },
            "ui": {"theme": "dark", "window_width": 1400, "window_height": 900},
            "paths": {"output_folder": "", "last_opened": ""}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get nested config value using dot notation"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set nested config value using dot notation"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self._save()
```

### 3. [ ] Tạo Database Manager (src/data/database.py)

```python
"""SQLite Database Manager"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.utils.constants import DATABASE_FILE

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance
    
    def _init_db(self) -> None:
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create required tables"""
        cursor = self.conn.cursor()
        
        # History table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                prompt TEXT,
                outline_json TEXT,
                template_name TEXT,
                output_path TEXT,
                slide_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT,
                description TEXT,
                category TEXT,
                preview_path TEXT,
                config_json TEXT,
                is_builtin BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def add_history(self, title: str, prompt: str, outline_json: str,
                    template_name: str, output_path: str, slide_count: int) -> int:
        """Add new history entry"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO history (title, prompt, outline_json, template_name, 
                                output_path, slide_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, prompt, outline_json, template_name, output_path, slide_count))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get recent history entries"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM history ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_history(self, history_id: int) -> None:
        """Delete history entry"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
        self.conn.commit()
```

### 4. [ ] Tạo Data Models (src/data/models.py)

```python
"""Data Models for SlideGenius"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class SlideType(Enum):
    TITLE = "title"
    CONTENT = "content"
    BULLET = "bullet"
    IMAGE_TEXT = "image_text"
    CHART = "chart"
    QUOTE = "quote"
    COMPARISON = "comparison"
    TIMELINE = "timeline"

@dataclass
class SlideItem:
    """Single slide in outline"""
    title: str
    content: List[str] = field(default_factory=list)
    slide_type: SlideType = SlideType.CONTENT
    speaker_notes: str = ""
    image_prompt: Optional[str] = None

@dataclass
class Outline:
    """Complete presentation outline"""
    title: str
    slides: List[SlideItem] = field(default_factory=list)
    language: str = "vi"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "title": self.title,
            "language": self.language,
            "slides": [
                {
                    "title": s.title,
                    "content": s.content,
                    "slide_type": s.slide_type.value,
                    "speaker_notes": s.speaker_notes,
                    "image_prompt": s.image_prompt
                }
                for s in self.slides
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Outline':
        """Create Outline from dictionary"""
        slides = [
            SlideItem(
                title=s["title"],
                content=s.get("content", []),
                slide_type=SlideType(s.get("slide_type", "content")),
                speaker_notes=s.get("speaker_notes", ""),
                image_prompt=s.get("image_prompt")
            )
            for s in data.get("slides", [])
        ]
        return cls(
            title=data["title"],
            slides=slides,
            language=data.get("language", "vi")
        )

@dataclass
class Template:
    """Presentation template"""
    name: str
    display_name: str
    description: str
    category: str
    preview_path: str
    primary_color: str
    secondary_color: str
    accent_color: str
    font_heading: str = "Arial"
    font_body: str = "Arial"
```

### 5. [ ] Tạo AI Service (src/core/ai_service.py)

```python
"""AI Service - Gemini API Integration"""
import json
import google.generativeai as genai
from typing import Optional
from src.data.config_manager import ConfigManager
from src.data.models import Outline, SlideItem, SlideType

class AIService:
    def __init__(self):
        self.config = ConfigManager()
        self._configure_api()
    
    def _configure_api(self) -> None:
        """Configure Gemini API with key from config"""
        api_key = self.config.get("api.gemini_key", "")
        if api_key:
            genai.configure(api_key=api_key)
            model_name = self.config.get("api.model", "gemini-1.5-flash")
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
    
    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return self.model is not None
    
    def generate_outline(self, prompt: str, num_slides: int = 8) -> Optional[Outline]:
        """Generate presentation outline from prompt"""
        if not self.is_configured():
            raise ValueError("API key not configured. Please set in Settings.")
        
        system_prompt = f'''Bạn là chuyên gia tạo slide thuyết trình.
Tạo outline cho bài thuyết trình với {num_slides} slides dựa trên yêu cầu của user.

Trả về JSON theo format sau (KHÔNG có markdown code block):
{{
    "title": "Tiêu đề bài thuyết trình",
    "language": "vi",
    "slides": [
        {{
            "title": "Tiêu đề slide",
            "content": ["Điểm 1", "Điểm 2", "Điểm 3"],
            "slide_type": "title|content|bullet|quote",
            "speaker_notes": "Ghi chú cho người thuyết trình"
        }}
    ]
}}

Quy tắc:
- Slide đầu tiên luôn là slide_type: "title"
- Slide cuối cùng là tổng kết hoặc Q&A
- Mỗi slide content có 3-5 bullet points
- Nội dung ngắn gọn, súc tích
- Phù hợp với context của prompt
'''
        
        try:
            response = self.model.generate_content(
                f"{system_prompt}\n\nYêu cầu: {prompt}",
                generation_config=genai.GenerationConfig(
                    temperature=self.config.get("generation.creativity_level", 70) / 100,
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON response
            data = json.loads(response.text)
            return Outline.from_dict(data)
            
        except Exception as e:
            print(f"AI Error: {e}")
            return None
    
    def test_connection(self) -> tuple[bool, str]:
        """Test API connection"""
        if not self.is_configured():
            return False, "API key not configured"
        
        try:
            response = self.model.generate_content("Say 'OK' if you can hear me.")
            return True, "Connection successful!"
        except Exception as e:
            return False, str(e)
```

### 6. [ ] Update **init**.py files

Đảm bảo các package có thể import được.

---

## 📁 Files to Create/Modify

| File | Purpose |
|------|---------|
| `src/utils/constants.py` | App constants |
| `src/data/config_manager.py` | Config read/write |
| `src/data/database.py` | SQLite operations |
| `src/data/models.py` | Data models |
| `src/core/ai_service.py` | Gemini API |

---

## 🧪 Test Criteria

- [ ] ConfigManager đọc/ghi config.json thành công
- [ ] DatabaseManager tạo tables thành công
- [ ] Có thể add và get history
- [ ] AIService.test_connection() trả về kết quả
- [ ] Outline.to_dict() và from_dict() hoạt động đúng

---

## 📝 Notes

- API key sẽ được nhập từ Settings dialog (Phase 04)
- Chưa cần handle tất cả error cases
- Focus: Core logic hoạt động ổn định

---

**Next Phase:** [Phase 03 - Main UI Shell](phase-03-ui-shell.md)
