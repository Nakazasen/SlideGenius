import unittest
from unittest.mock import MagicMock, call, patch

from src.core.model_cascade import ModelCascade, ModelConfig


class TestKeyRotation(unittest.TestCase):
    def setUp(self):
        self.cascade = ModelCascade()
        self.cascade.api_keys = ["key-1", "key-2"]
        self.cascade.current_key_index = 0
        self.cascade.models = [ModelConfig("test-model", timeout=1)]

    @patch("src.core.model_cascade.genai.Client")
    def test_normal_generation(self, mock_client_class):
        """Use a fake google.genai client; no live Gemini call is made."""
        mock_response = MagicMock()
        mock_response.text = "Success"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        response = self.cascade.generate_content("test prompt")

        mock_client_class.assert_called_once_with(api_key="key-1")
        mock_client.models.generate_content.assert_called_once_with(
            model="test-model",
            contents="test prompt",
            config=None,
        )
        self.assertEqual(response.text, "Success")

    @patch("src.core.model_cascade.genai.Client")
    def test_rotation_on_quota_error(self, mock_client_class):
        """Rotate to key-2 when key-1 hits quota, using fake clients only."""
        mock_response = MagicMock()
        mock_response.text = "Success on Key 2"

        key_1_client = MagicMock()
        key_1_client.models.generate_content.side_effect = RuntimeError("429 quota exceeded")
        key_2_client = MagicMock()
        key_2_client.models.generate_content.return_value = mock_response
        mock_client_class.side_effect = [key_1_client, key_2_client]

        response = self.cascade.generate_content("test prompt")

        mock_client_class.assert_has_calls([call(api_key="key-1"), call(api_key="key-2")])
        self.assertEqual(response.text, "Success on Key 2")
        self.assertEqual(self.cascade.current_key_index, 1)

    @patch("src.core.model_cascade.genai.Client")
    def test_all_keys_exhausted(self, mock_client_class):
        """Raise after all configured keys hit quota without network access."""
        key_1_client = MagicMock()
        key_1_client.models.generate_content.side_effect = RuntimeError("429 quota exceeded")
        key_2_client = MagicMock()
        key_2_client.models.generate_content.side_effect = RuntimeError("429 quota exceeded")
        mock_client_class.side_effect = [key_1_client, key_2_client]

        with self.assertRaises(RuntimeError):
            self.cascade.generate_content("test prompt")

        mock_client_class.assert_has_calls([call(api_key="key-1"), call(api_key="key-2")])


if __name__ == "__main__":
    unittest.main()
