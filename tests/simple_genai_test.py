import os
import sys

print("1. Importing google.genai...")
try:
    from google import genai
    print("   Success!")
except ImportError as e:
    print(f"   Failed: {e}")
    sys.exit(1)

print("2. checking google-genai version...")
# Try checking pip output via subprocess if needed, but import is key
import subprocess
try:
    subprocess.run([sys.executable, "-m", "pip", "show", "google-genai"], check=True)
except Exception:
    print("   Pip check failed")

print("3. Done with minimal check.")
