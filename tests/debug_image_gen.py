"""Debug script for Image Generator."""
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd()))

# Configure logging
logging.basicConfig(level=logging.INFO)

from src.core.image_generator import ImageGenerator

def test_generation():
    print("Initializing ImageGenerator...")
    generator = ImageGenerator()
    
    print(f"API Keys loaded: {len(generator.api_keys)}")
    
    prompt = "A futuristic city with flying cars, cyberpunk style"
    print(f"\nTesting generation with prompt: '{prompt}'")
    
    # Force test Gemini Native
    print("\n--- Testing Gemini Native ---")
    try:
        # We'll peek into private method for debugging
        result = generator._generate_via_gemini_native(prompt, Path("test_gemini.png"))
        print(f"Gemini Native Result: {result}")
    except Exception as e:
        print(f"Gemini Native Exception: {e}")

    # Force test Pollinations
    print("\n--- Testing Pollinations ---")
    try:
        result = generator._generate_via_pollinations(prompt, Path("test_pollinations.png"))
        print(f"Pollinations Result: {result}")
    except Exception as e:
        print(f"Pollinations Exception: {e}")

if __name__ == "__main__":
    test_generation()
