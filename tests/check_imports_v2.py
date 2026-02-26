import sys
import os

sys.path.append(os.getcwd())

def log(msg):
    print(msg, flush=True)

log("1. Checking src.data.templates...")
try:
    from src.data.templates import TEMPLATE_LIST
    log("   OK")
except Exception as e:
    log(f"   FAIL: {e}")

log("2. Checking src.ui.components.input_panel...")
try:
    from src.ui.components.input_panel import InputPanel
    log("   OK")
except Exception as e:
    log(f"   FAIL: {e}")

log("3. Checking src.ui.screens.home_screen...")
try:
    from src.ui.screens.home_screen import HomeScreen
    log("   OK")
except Exception as e:
    log(f"   FAIL: {e}")

log("4. Checking src.app...")
try:
    from src.app import SlideGeniusApp
    log("   OK")
except Exception as e:
    log(f"   FAIL: {e}")
