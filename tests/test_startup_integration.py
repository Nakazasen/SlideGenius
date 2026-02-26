
import sys
import os
import pytest
# Add root to path
sys.path.append(os.getcwd())

def test_imports_and_instantiation():
    """Verify that core components can be imported and instantiated without crashing."""
    print("Testing ImageGenerator instantiation...")
    from src.core.image_generator import ImageGenerator
    img_gen = ImageGenerator()
    assert img_gen is not None
    print("ImageGenerator OK")
    
    print("Testing AIService instantiation...")
    from src.core.ai_service import AIService
    ai_service = AIService()
    assert ai_service is not None
    print("AIService OK")
    
    print("Testing ModelCascade instantiation...")
    from src.core.model_cascade import ModelCascade
    cascade = ModelCascade()
    assert cascade is not None
    print("ModelCascade OK")

    print("Testing SlideGeniusApp Import...")
    from src.app import SlideGeniusApp
    assert SlideGeniusApp is not None
    print("SlideGeniusApp Import OK")

if __name__ == "__main__":
    test_imports_and_instantiation()
