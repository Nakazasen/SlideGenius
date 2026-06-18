from pathlib import Path

import pytest

from src.core.image_generator import ImageGenerator


class OfflineImageGenerator(ImageGenerator):
    """ImageGenerator variant that writes only to pytest temp folders."""

    def __init__(self, output_dir: Path):
        super().__init__()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_via_pollinations(self, prompt: str, output_path: Path):
        return None

    def _generate_via_picsum(self, output_path: Path):
        return None


def test_imagen_placeholder_uses_tmp_path(tmp_path: Path):
    """Default test must not call live image services or write tracked assets."""
    generator = OfflineImageGenerator(tmp_path)

    output_path = generator.generate_image(
        "A futuristic eco-friendly city with flying lush green islands.",
        "test_imagen_city.png",
    )

    generated = Path(output_path)
    assert generated.exists()
    assert generated.parent == tmp_path
    assert generated.name == "test_imagen_city.png"
    assert generated.stat().st_size > 0


@pytest.mark.integration
@pytest.mark.live_provider
def test_imagen_live_provider(tmp_path: Path):
    """Optional live image-provider check; skipped by default."""
    pytest.skip("Live image provider checks require explicit credentials/network and are not unit tests.")
