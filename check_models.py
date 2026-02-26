
import os
import sys
from google import genai
from src.data.config_manager import ConfigManager

def check_models():
    config = ConfigManager()
    api_key = config.get("api.gemini_key")
    
    if not api_key:
        print("No API Key found in config.")
        return

    client = genai.Client(api_key=api_key)
    
    print("--- Available Models ---")
    try:
        # Check if list_models is the correct method name or similar
        # Inspecting directory first if unsure, but standard is models.list()
        for m in client.models.list():
            print(f"Name: {m.name}")
            print(f"Display Name: {m.display_name}")
            print(f"Supported Generation Methods: {m.supported_generation_methods}")
            print("-" * 20)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    check_models()
