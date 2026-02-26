
import unittest
from unittest.mock import MagicMock, patch, call
from src.core.model_cascade import ModelCascade, ModelConfig
import google.generativeai as genai
from google.api_core import exceptions

class TestKeyRotation(unittest.TestCase):
    
    def setUp(self):
        # Reset singleton or mock config
        self.cascade = ModelCascade()
        # Override keys
        self.cascade.api_keys = ["key-1", "key-2"]
        self.cascade.current_key_index = 0
        # Override models to just 1 for testing rotation logic
        self.cascade.models = [ModelConfig("test-model", timeout=1)]
        
    @patch("src.core.model_cascade.genai")
    def test_normal_generation(self, mock_genai):
        """Test simple generation using first key."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Success"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        response = self.cascade.generate_content("test prompt")
        
        # Should configure with key-1
        mock_genai.configure.assert_called_with(api_key="key-1")
        self.assertEqual(response.text, "Success")
        
    @patch("src.core.model_cascade.genai")
    def test_rotation_on_quota_error(self, mock_genai):
        """Test rotation to key-2 when key-1 hits quota limit."""
        mock_model = MagicMock()
        
        # First call raises ResourceExhausted, Second succeeds
        mock_response = MagicMock()
        mock_response.text = "Success on Key 2"
        
        # Side effect for generate_content
        # We need to simulate that the FIRST call (with Key 1) fails, 
        # and the SECOND call (with Key 2) succeeds.
        # Since we create a NEW model instance each time in the loop, logic handles it.
        # But mock_genai.GenerativeModel() returns a mock object.
        
        # Issue: The code calls GenerativeModel(id) inside the loop.
        # So we can set side_effect on the mock_model instance's generate_content method?
        # BUT if it returns the SAME mock object, side_effect iterator works.
        mock_model.generate_content.side_effect = [
            exceptions.ResourceExhausted("Quota exceeded"), # 1st call (Key 1)
            mock_response # 2nd call (Key 2)
        ]
        
        mock_genai.GenerativeModel.return_value = mock_model
        
        response = self.cascade.generate_content("test prompt")
        
        # Check configuration calls
        # Should have called configure with Key 1, then Key 2
        calls = [call(api_key="key-1"), call(api_key="key-2")]
        mock_genai.configure.assert_has_calls(calls)
        
        self.assertEqual(response.text, "Success on Key 2")
        
    @patch("src.core.model_cascade.genai")
    def test_all_keys_exhausted(self, mock_genai):
        """Test failure when ALL keys hit quota limit."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = exceptions.ResourceExhausted("Quota exceeded")
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Expect error after trying all keys
        with self.assertRaises(Exception):
            self.cascade.generate_content("test prompt")
            
        # Should have tried both keys
        calls = [call(api_key="key-1"), call(api_key="key-2")]
        mock_genai.configure.assert_has_calls(calls)

if __name__ == '__main__':
    unittest.main()
