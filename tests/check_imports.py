import sys
import os

# Add project root
sys.path.append(os.getcwd())

print("1. Checking src.data.templates...")
try:
    from src.data.templates import TEMPLATE_LIST
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")

print("2. Checking src.ui.components.input_panel...")
try:
    from src.ui.components.input_panel import InputPanel
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")

print("3. Checking src.ui.screens.home_screen...")
try:
    from src.ui.screens.home_screen import HomeScreen
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")

print("4. Checking src.app...")
try:
    from src.app import SlideGeniusApp
    print("   OK")
except Exception as e:
    print(f"   FAIL: {e}")
