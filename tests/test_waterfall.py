"""Unit tests and optional live scan for the AI waterfall strategy."""
import logging
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.ai_service import AIService
from src.core.model_cascade import ModelCascade, ModelConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TestWaterfallStrategy(unittest.TestCase):
    def setUp(self):
        self.cascade = ModelCascade()
        self.cascade.models = [
            ModelConfig(model_id="test-model-1", timeout=1, is_active=True),
            ModelConfig(model_id="test-model-2", timeout=1, is_active=True),
            ModelConfig(model_id="test-model-3", timeout=1, is_active=True),
        ]
        self.cascade.api_keys = ["unit-test-key"]
        self.cascade.current_key_index = 0

    @patch("src.core.model_cascade.genai.Client")
    def test_fallback_success_first_try(self, mock_client_class):
        """Test success on first model with a fake google.genai client."""
        mock_response = MagicMock()
        mock_response.text = "Success"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        response = self.cascade.generate_content("test prompt")

        self.assertEqual(response.text, "Success")
        mock_client_class.assert_called_once_with(api_key="unit-test-key")
        mock_client.models.generate_content.assert_called_once_with(
            model="test-model-1",
            contents="test prompt",
            config=None,
        )

    @patch("src.core.model_cascade.genai.Client")
    def test_fallback_on_error(self, mock_client_class):
        """Test model fallback when the first model fails."""
        mock_response = MagicMock()
        mock_response.text = "Success via Fallback"
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            RuntimeError("Timeout"),
            mock_response,
        ]
        mock_client_class.return_value = mock_client

        response = self.cascade.generate_content("test prompt")

        self.assertEqual(response.text, "Success via Fallback")
        self.assertEqual(mock_client.models.generate_content.call_count, 2)
        self.assertEqual(
            [c.kwargs["model"] for c in mock_client.models.generate_content.mock_calls],
            ["test-model-1", "test-model-2"],
        )

    @patch("src.core.model_cascade.genai.Client")
    def test_all_models_fail(self, mock_client_class):
        """Test failure after all models fail without contacting a provider."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("All failed")
        mock_client_class.return_value = mock_client

        with self.assertRaises(RuntimeError):
            self.cascade.generate_content("test prompt")

        self.assertEqual(mock_client.models.generate_content.call_count, 3)
        self.assertEqual(
            [c.kwargs["model"] for c in mock_client.models.generate_content.mock_calls],
            ["test-model-1", "test-model-2", "test-model-3"],
        )


@pytest.mark.integration
@pytest.mark.live_provider
def test_scan_available_models_live_provider():
    """Manual live connectivity check; skipped unless RUN_LIVE_PROVIDER_TESTS=1."""
    if os.getenv("RUN_LIVE_PROVIDER_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_PROVIDER_TESTS=1 and configure Gemini keys to run live scan.")
    scan_available_models()


def scan_available_models():
    """Manual connectivity check (requires real API key)."""
    print("\n=== SCANNING AVAILABLE MODELS ===")
    ai = AIService()
    if not ai.is_configured():
        pytest.skip("API key not configured. Skipping live scan.")

    cascade = ModelCascade()
    print(f"Found {len(cascade.models)} configured models.")

    print(f"{'#':<3} {'Model ID':<40} {'Timeout':<10} {'Active':<8} {'Status'}")
    print("-" * 80)

    from google import genai

    api_key = cascade._get_current_key()
    if not api_key:
        pytest.skip("No Gemini API key configured. Skipping live scan.")

    client = genai.Client(api_key=api_key)
    for idx, model_cfg in enumerate(cascade.models):
        status = "..."
        if not model_cfg.is_active:
            status = "SKIP (Inactive)"
            print(f"{idx + 1:<3} {model_cfg.model_id:<40} {model_cfg.timeout:<10} {str(model_cfg.is_active):<8} {status}")
            continue

        try:
            response = client.models.generate_content(
                model=model_cfg.model_id,
                contents="hi",
            )
            if response:
                status = "OK"
        except Exception as e:
            err = str(e)
            if "404" in err:
                status = "Not Found"
            elif "403" in err:
                status = "Permission Denied"
            else:
                status = f"Error: {err[:30]}..."

        print(f"{idx + 1:<3} {model_cfg.model_id:<40} {model_cfg.timeout:<10} {str(model_cfg.is_active):<8} {status}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scan":
        scan_available_models()
    else:
        unittest.main()
