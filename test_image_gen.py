
import sys
import os
# Add root to path
sys.path.append(os.getcwd())

from src.core.image_generator import ImageGenerator
import time

def test_generation():
    print("Initializing ImageGenerator...")
    try:
        gen = ImageGenerator()
        print("Generator initialized.")
        
        prompt = "A beautiful futuristic city with flying cars, digital art style"
        print(f"Generating image for prompt: '{prompt}'")
        
        start_time = time.time()
        path = gen.generate_image(prompt, filename=f"test_gen_{int(start_time)}.png")
        end_time = time.time()
        
        if path and os.path.exists(path):
            print(f"SUCCESS! Image generated at: {path}")
            print(f"Time taken: {end_time - start_time:.2f}s")
            print(f"File size: {os.path.getsize(path)} bytes")
        else:
            print("FAILURE: No image generated or file missing.")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
