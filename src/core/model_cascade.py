"""Model Cascade - Waterfall Strategy for Gemini Models."""
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
try:
    # FORCE DISABLE: google.genai hangs on import
    raise ImportError("Disabled due to hang")
    from google import genai
    from google.genai import types
except ImportError:
    # Fallback for old SDK or missing package
    import google.generativeai as genai
    types = None # Types not available in old SDK in same way
from src.data.config_manager import ConfigManager
from src.utils.logger import get_logger

# Get logger
logger = get_logger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a single AI model."""
    model_id: str
    timeout: int = 10
    is_active: bool = True
    
    @property
    def display_name(self) -> str:
        """Friendly name for UI."""
        return self.model_id.replace("-", " ").title()

class ModelCascade:
    """Manages waterfall strategy for AI model selection."""
    
    DEFAULT_MODELS = [
        # Top Tier
        ModelConfig("gemini-2.0-flash", timeout=15),
        ModelConfig("gemini-1.5-pro", timeout=20),
        ModelConfig("gemini-1.5-flash", timeout=10),
    ]

    def __init__(self):
        self.config_manager = ConfigManager()
        self.api_keys: List[str] = []
        self.current_key_index: int = 0
        self._reload_config()

    def _reload_config(self):
        """Reload configuration and model list."""
        self.api_keys = self.config_manager.get("api.gemini_keys", [])
        # Fallback to single key if list is empty
        if not self.api_keys:
            single_key = self.config_manager.get("api.gemini_key", "")
            if single_key:
                self.api_keys = [single_key]
        
        self.current_key_index = 0
        
        # Load strategy from config, or use default if empty
        saved_strategy = self.config_manager.get("api.waterfall_strategy", [])
        
        if saved_strategy:
            # Reconstruct ModelConfig objects from list of dicts
            self.models = [ModelConfig(**m) for m in saved_strategy]
        else:
            self.models = self.DEFAULT_MODELS
            # Save defaults to config so UI has something to show/edit
            self._save_defaults()
            
    def _save_defaults(self):
        """Save default models to config."""
        strategy_data = [
            {"model_id": m.model_id, "timeout": m.timeout, "is_active": m.is_active}
            for m in self.DEFAULT_MODELS
        ]
        self.config_manager.set("api.waterfall_strategy", strategy_data)

    def configure_api(self, api_keys: List[str]):
        """Update API keys."""
        self.api_keys = api_keys
        self.current_key_index = 0

    def _get_current_key(self) -> Optional[str]:
        """Get currently active API key."""
        if not self.api_keys:
            return None
        return self.api_keys[self.current_key_index % len(self.api_keys)]

    def _rotate_key(self):
        """Switch to next API key."""
        if self.api_keys:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            logger.info(f"Rotated to API Key index: {self.current_key_index}")

    def get_active_models(self) -> List[ModelConfig]:
        """Return list of active text-generation models."""
        return [m for m in self.models if m.is_active]

    def generate_content(self, prompt: str, generation_config: Optional[Any] = None) -> Any:
        """
        Execute Waterfall Strategy:
        Try models sequentially. If one fails/timeouts, try the next.
        Handles API Key rotation on Quota Errors.
        """
        if not self.api_keys:
            raise ValueError("No API Keys configured")

        active_models = self.get_active_models()
        last_error = None
        
        logger.info(f"Starting Waterfall Generation with {len(active_models)} models and {len(self.api_keys)} keys")

        for model_cfg in active_models:
            logger.info(f"Trying model: {model_cfg.model_id} (Timeout: {model_cfg.timeout}s)")
            
            # Key Rotation Loop for current model
            keys_tried = 0
            while keys_tried < len(self.api_keys):
                current_key = self._get_current_key()
                if not current_key:
                    break # No more keys to try
                
                try:
                    # CHECK SDK VERSION - Using 'types' variable as it's only set in new SDK path
                    if types is not None:
                        # === NEW SDK (google-genai) ===
                        client = genai.Client(api_key=current_key)
                        response = client.models.generate_content(
                            model=model_cfg.model_id,
                            contents=prompt,
                            config=generation_config
                        )
                    else:
                        # === OLD SDK (google-generativeai) ===
                        genai.configure(api_key=current_key)
                        model = genai.GenerativeModel(model_cfg.model_id)
                        
                        # Convert config if needed, or pass validation
                        # Old SDK expects generation_config as dict or GenerationConfig object
                        response = model.generate_content(
                            prompt,
                            generation_config=generation_config
                        )
                    
                    logger.info(f"SUCCESS: {model_cfg.model_id}")
                    return response

                except Exception as e:
                    error_msg = str(e)
                    logger.warning(f"FAILED: {model_cfg.model_id} - {error_msg}")
                    
                    # Check for quota errors (429)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        logger.warning(f"Key {self.current_key_index} quota exhausted on {model_cfg.model_id}. Rotating key.")
                        self._rotate_key()
                        keys_tried += 1
                        last_error = e
                        continue 
                        
                    last_error = e
                    break # Break inner loop, go to NEXT MODEL
            
            continue

        # If all failed
        logger.error("All models failed.")
        if last_error:
            raise last_error
        raise RuntimeError("Waterfall failed: No active models available")
