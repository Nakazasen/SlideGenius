"""Verification Script for AI Waterfall Strategy."""
import sys
import unittest
import logging
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.model_cascade import ModelCascade, ModelConfig
from src.core.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestWaterfallStrategy(unittest.TestCase):
    
    def setUp(self):
        self.cascade = ModelCascade()
        # Mock Default Models to a smaller set for testing logic
        self.cascade.models = [
            ModelConfig(model_id="test-model-1", timeout=1, is_active=True),
            ModelConfig(model_id="test-model-2", timeout=1, is_active=True),
            ModelConfig(model_id="test-model-3", timeout=1, is_active=True)
        ]
        self.cascade.api_key = "TEST_API_KEY"

    @patch("google.generativeai.GenerativeModel")
    def test_fallback_success_first_try(self, mock_model_class):
        """Test success on first model."""
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = "Success"
        mock_model_class.return_value = mock_instance
        
        response = self.cascade.generate_content("test prompt")
        
        self.assertEqual(response.text, "Success")
        # Should only try the first model
        self.assertEqual(mock_model_class.call_count, 1)

    @patch("google.generativeai.GenerativeModel")
    def test_fallback_on_error(self, mock_model_class):
        """Test fallback when first model fails."""
        # Setup mock to fail first time, succeed second time
        mock_instance_1 = MagicMock()
        mock_instance_1.generate_content.side_effect = Exception("Timeout")
        
        mock_instance_2 = MagicMock()
        mock_instance_2.generate_content.return_value.text = "Success via Fallback"
        
        # We need side_effect for the constructor to return different instances
        mock_model_class.side_effect = [mock_instance_1, mock_instance_2, MagicMock()]
        
        response = self.cascade.generate_content("test prompt")
        
        self.assertEqual(response.text, "Success via Fallback")
        # Should try 2 models
        self.assertEqual(mock_model_class.call_count, 2)
        
    @patch("google.generativeai.GenerativeModel")
    def test_all_models_fail(self, mock_model_class):
        """Test when everyone fails."""
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = Exception("All failed")
        mock_model_class.return_value = mock_instance
        
        with self.assertRaises(Exception):
            self.cascade.generate_content("test prompt")
            
        # Should try all 3 models
        self.assertEqual(mock_model_class.call_count, 3)

def scan_available_models():
    """Manual connectivity check (requires real API key)."""
    print("\n=== SCANNING AVAILABLE MODELS ===")
    ai = AIService()
    if not ai.is_configured():
        print("❌ API Key not configured. Skipping live scan.")
        return
    
    cascade = ModelCascade()
    print(f"Found {len(cascade.models)} configured models.")
    
    print(f"{'#':<3} {'Model ID':<40} {'Timeout':<10} {'Active':<8} {'Status'}")
    print("-" * 80)
    
    import google.generativeai as genai
    
    for idx, model_cfg in enumerate(cascade.models):
        status = "..."
        if not model_cfg.is_active:
            status = "SKIP (Inactive)"
            print(f"{idx+1:<3} {model_cfg.model_id:<40} {model_cfg.timeout:<10} {str(model_cfg.is_active):<8} {status}")
            continue
            
        try:
            model = genai.GenerativeModel(model_cfg.model_id)
            # Just init is often enough to check valid name, 
            # but generate is needed to check access
            # We use a very cheap tokens prompt
            response = model.generate_content("hi", request_options={'timeout': 5})
            if response:
                 status = "✅ OK"
        except Exception as e:
            err = str(e)
            if "404" in err:
                status = "❌ Not Found"
            elif "403" in err:
                status = "⛔ Permission Denied" 
            else:
                status = f"⚠️ Error: {err[:30]}..."
                
        print(f"{idx+1:<3} {model_cfg.model_id:<40} {model_cfg.timeout:<10} {str(model_cfg.is_active):<8} {status}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scan":
        scan_available_models()
    else:
        unittest.main()
