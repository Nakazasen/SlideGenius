from pathlib import Path

from src.core.image_generator import ImageGenerator


class OfflineImageGenerator(ImageGenerator):
    """Offline test generator that only writes to a pytest temporary directory."""

    def __init__(self, output_dir: Path):
        super().__init__()
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _generate_via_pollinations(self, prompt: str, output_path: Path):
        return None

    def _generate_via_picsum(self, output_path: Path):
        return None


def test_generation_uses_placeholder_in_tmp_path(tmp_path: Path):
    """Default image-generation test must not call network or write repo assets."""
    generator = OfflineImageGenerator(tmp_path)

    output_path = Path(
        generator.generate_image(
            "A beautiful futuristic city with flying cars, digital art style",
            filename="test_gen_offline.png",
        )
    )

    assert output_path.exists()
    assert output_path.parent == tmp_path
    assert output_path.name == "test_gen_offline.png"
    assert output_path.stat().st_size > 0
