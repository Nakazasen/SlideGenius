"""Model Cascade - Waterfall Strategy for Gemini text models."""
from dataclasses import dataclass
from typing import Any, List, Optional

from google import genai
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

    BLOCKED_MODEL_TOKENS = (
        "tts",
        "audio",
        "imagen",
        "veo",
        "computer-use",
    )
    
    DEFAULT_MODELS = [
        ModelConfig("gemma-3-27b-it", timeout=18),
        ModelConfig("gemma-4-26b-a4b-it", timeout=18),
        ModelConfig("gemma-3n-e4b-it", timeout=14),
        ModelConfig("gemma-3-4b-it", timeout=12),
        ModelConfig("gemini-robotics-er-1.5-preview", timeout=20),
        ModelConfig("gemma-3-12b-it", timeout=16),
        ModelConfig("gemma-3n-e2b-it", timeout=12),
        ModelConfig("gemma-3-1b-it", timeout=10),
        ModelConfig("gemini-2.5-flash", timeout=12),
        ModelConfig("gemini-2.5-flash-lite", timeout=9),
        ModelConfig("gemma-4-31b-it", timeout=18),
        ModelConfig("gemini-3-flash-preview", timeout=12),
        ModelConfig("gemini-3.1-flash-lite", timeout=9),
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
            self.models = self._sanitize_models([ModelConfig(**m) for m in saved_strategy])
        else:
            self.models = self.DEFAULT_MODELS
            # Save defaults to config so UI has something to show/edit
            self._save_defaults()

        if not self.models:
            self.models = self.DEFAULT_MODELS
            self._save_defaults()
            
    def _save_defaults(self):
        """Save default models to config."""
        strategy_data = [
            {"model_id": m.model_id, "timeout": m.timeout, "is_active": m.is_active}
            for m in self._sanitize_models(self.DEFAULT_MODELS)
        ]
        self.config_manager.set("api.waterfall_strategy", strategy_data)

    def _sanitize_models(self, models: List[ModelConfig]) -> List[ModelConfig]:
        """Keep only text-generation models that make sense for this app."""
        sanitized: List[ModelConfig] = []
        seen = set()
        for model in models:
            model_id = (model.model_id or "").strip()
            lowered = model_id.lower()
            if not model_id or model_id in seen:
                continue
            if any(token in lowered for token in self.BLOCKED_MODEL_TOKENS):
                logger.warning("Skipping unsupported model in waterfall strategy: %s", model_id)
                continue
            seen.add(model_id)
            sanitized.append(ModelConfig(model_id=model_id, timeout=model.timeout, is_active=model.is_active))
        return sanitized

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

    def generate_content(self, prompt: str, generation_config: Optional[Any] = None, progress_callback=None) -> Any:
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
        if progress_callback:
            progress_callback(f"Đang thử {len(active_models)} model theo thứ tự ưu tiên...")

        for model_cfg in active_models:
            logger.info(f"Trying model: {model_cfg.model_id} (Timeout: {model_cfg.timeout}s)")
            if progress_callback:
                progress_callback(f"Đang thử model {model_cfg.model_id}...")
            
            # Key Rotation Loop for current model
            keys_tried = 0
            while keys_tried < len(self.api_keys):
                current_key = self._get_current_key()
                if not current_key:
                    break # No more keys to try
                
                try:
                    client = genai.Client(api_key=current_key)
                    response = client.models.generate_content(
                        model=model_cfg.model_id,
                        contents=prompt,
                        config=generation_config
                    )
                    
                    logger.info(f"SUCCESS: {model_cfg.model_id}")
                    if progress_callback:
                        progress_callback(f"Đã nhận phản hồi từ model {model_cfg.model_id}.")
                    return response

                except Exception as e:
                    error_msg = str(e)
                    logger.warning(f"FAILED: {model_cfg.model_id} - {error_msg}")
                    
                    # Check for quota errors (429)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        if progress_callback:
                            progress_callback(f"Model {model_cfg.model_id} quá quota, chuyển model khác...")
                        logger.warning(f"Key {self.current_key_index} quota exhausted on {model_cfg.model_id}. Rotating key.")
                        self._rotate_key()
                        keys_tried += 1
                        last_error = e
                        continue 
                        
                    last_error = e
                    if progress_callback:
                        progress_callback(f"Model {model_cfg.model_id} lỗi hoặc quá tải, chuyển model khác...")
                    break # Break inner loop, go to NEXT MODEL
            
            continue

        # If all failed
        logger.error("All models failed.")
        if last_error:
            raise last_error
        raise RuntimeError("Waterfall failed: No active models available")
