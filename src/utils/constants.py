import sys
import os
from pathlib import Path

# Paths
# Bundle awareness: PyInstaller creates a temp folder and stores path in _MEIPASS
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    APP_DIR = Path(sys._MEIPASS)
else:
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
