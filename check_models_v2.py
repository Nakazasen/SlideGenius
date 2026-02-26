
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from google import genai
    print("Successfully imported google.genai")
except ImportError as e:
    print(f"Failed to import google.genai: {e}")
    # Try alternate import
    try:
        import google.genai
        print("Successfully imported google.genai directly")
    except ImportError as e2:
        print(f"Failed direct import too: {e2}")

from src.data.config_manager import ConfigManager

def check_models():
    print("Initializing ConfigManager...")
    config = ConfigManager()
    api_key = config.get("api.gemini_key")
    
    if not api_key:
        print("No API Key found.")
        return

    print(f"Using API Key: {api_key[:5]}...")
    
    try:
        client = genai.Client(api_key=api_key)
        print("Client created. Listing models...")
        
        # Pager for models
        # Note: The SDK might yield pages
        for m in client.models.list():
            print(f"Model: {m.name}")
            print(f"Methods: {m.supported_generation_methods}")
            # Check for image generation capability
            if "generateImages" in m.supported_generation_methods or "image" in str(m.supported_generation_methods).lower():
                print(">>> SUPPORTS IMAGES <<<")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error during API call: {e}")

if __name__ == "__main__":
    check_models()
