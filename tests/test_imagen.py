import sys
import os
# Add project root
sys.path.append(os.getcwd())

from src.core.image_generator import ImageGenerator

def test_imagen():
    print("Testing Smart Illustrator (Imagen)...")
    
    generator = ImageGenerator()
    
    prompt = "A futuristic eco-friendly city with flying lush green islands, cinematic lighting, 8k resolution, photorealistic."
    print(f"Prompt: {prompt}")
    
    output_path = generator.generate_image(prompt, "test_imagen_city.png")
    
    if output_path:
        print(f"SUCCESS: Image saved to {output_path}")
        import os
        os.startfile(output_path)
    else:
        print("FAILURE: Could not generate image.")
        print("Note: This might happen if the API Key does not have access to Imagen 3 (Trusted Tester / Paid) or if the model name is incorrect in this region.")

if __name__ == "__main__":
    test_imagen()
