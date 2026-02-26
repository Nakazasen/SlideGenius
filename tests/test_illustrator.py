import sys
import os
# Add project root
sys.path.append(os.getcwd())

from pathlib import Path
from src.data.models import Outline, SlideItem, SlideType
from src.core.pptx_generator import PPTXGenerator

def test_illustrator_integration():
    print("Testing Smart Illustrator Integration...")
    
    # Create a mock Outline with a Content Slide + Image Prompt
    outline = Outline(
        title="Smart Illustrator Demo",
        slides=[
            SlideItem(title="Welcome to Future", slide_type=SlideType.TITLE),
            SlideItem(
                title="AI-Powered Cities",
                slide_type=SlideType.CONTENT,
                content=[
                    "Advanced sustainable infrastructure.",
                    "Flying autonomous vehicles.",
                    "Vertical gardens integration."
                ],
                image_prompt="A futuristic eco-friendly city with flying lush green islands, cinematic lighting, 8k resolution, photorealistic."
            ),
            SlideItem(
                title="Traditional Slide",
                slide_type=SlideType.CONTENT,
                content=["Just text here.", "No image."]
            )
        ]
    )
    
    # Generate PPTX
    generator = PPTXGenerator()
    output_path = Path("test_illustrator.pptx")
    generator.generate(outline, output_path)
    
    print(f"Generated: {output_path.absolute()}")
    import os
    os.startfile(output_path)

if __name__ == "__main__":
    test_illustrator_integration()
