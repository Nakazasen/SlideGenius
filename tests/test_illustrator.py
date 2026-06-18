from pathlib import Path

import pytest

from src.core.pptx_generator import PPTXGenerator
from src.data.models import Outline, SlideItem, SlideType


def test_illustrator_pptx_generation_uses_tmp_path(tmp_path: Path):
    """Render image-prompt slides without opening files or writing repo artifacts."""
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
                    "Vertical gardens integration.",
                ],
                image_prompt="A futuristic eco-friendly city with flying lush green islands, cinematic lighting, 8k resolution, photorealistic.",
            ),
            SlideItem(
                title="Traditional Slide",
                slide_type=SlideType.CONTENT,
                content=["Just text here.", "No image."],
            ),
        ],
    )

    output_path = tmp_path / "test_illustrator.pptx"
    PPTXGenerator().generate(outline, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


@pytest.mark.integration
def test_illustrator_manual_open_integration(tmp_path: Path):
    """Optional manual OS open check; skipped by default."""
    pytest.skip("Manual os.startfile check is intentionally excluded from default unit tests.")
