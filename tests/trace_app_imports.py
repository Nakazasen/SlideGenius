import sys
import os

sys.path.append(os.getcwd())

def log(msg):
    print(msg, flush=True)

log("STARTING IMPORT TRACE")

try:
    log("Importing ThemeManager...")
    from src.ui.theme_manager import ThemeManager
    log("OK")

    log("Importing Sidebar...")
    from src.ui.components.sidebar import Sidebar
    log("OK")

    log("Importing OutlineEditor...")
    from src.ui.components.outline_editor import OutlineEditor
    log("OK")

    log("Importing SettingsDialog...")
    from src.ui.dialogs.settings_dialog import SettingsDialog
    log("OK")

    log("Importing AIService...")
    from src.core.ai_service import AIService
    log("OK")

    log("Importing Outline...")
    from src.data.models import Outline
    log("OK")

    log("Importing Screens...")
    from src.ui.screens import HomeScreen, HistoryScreen, TemplatesScreen
    log("OK")

    log("Importing GenerateWorker...")
    from src.ui.workers import GenerateWorker
    log("OK")

    log("Importing TEMPLATE_LIST...")
    from src.data.templates import TEMPLATE_LIST
    log("OK")
    
except Exception as e:
    log(f"CRASH: {e}")
