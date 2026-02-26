from PIL import Image
import sys

try:
    img = Image.open("app_icon.png")
    img.save("app_icon.ico", format="ICO", sizes=[(256, 256)])
    print("Icon converted successfully")
except Exception as e:
    print(f"Error converting icon: {e}")
    sys.exit(1)
