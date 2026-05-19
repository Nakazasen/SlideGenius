"""Configuration Manager - Read/Write JSON config."""
import json
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from src.utils.constants import CONFIG_FILE


class ConfigManager:
    """Singleton class to manage application configuration."""
    
    _instance = None
    _config: dict = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            load_dotenv() # Load from .env if exists
            cls._instance._load()
        return cls._instance
    
    def _load(self) -> None:
        """Load config from file."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
                
            # Migration: Single Key -> List of Keys
            api_config = self._config.get("api", {})
            single_key = api_config.get("gemini_key", "")
            key_list = api_config.get("gemini_keys", [])
            
            if single_key and not key_list:
                api_config["gemini_keys"] = [single_key]
                self._save()

            generation_config = self._config.setdefault("generation", {})
            updated = False
            if "stable_mode" not in generation_config:
                generation_config["stable_mode"] = True
                updated = True
            if updated:
                self._save()
        else:
            self._config = self._default_config()
            self._save()
    
    def _save(self) -> None:
        """Save config to file."""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "version": "1.0.0",
            "api": {
                "gemini_key": "", # Deprecated, kept for backward compat
                "gemini_keys": [], # List of API keys for rotation
                "model": "gemma-3-27b-it",
                "waterfall_strategy": []
            },
            "generation": {
                "stable_mode": True,
                "creativity_level": 70,
                "auto_generate_images": False,
                "include_speaker_notes": True,
                "default_language": "vi",
                "enable_self_critique": False,
                "auto_retry_low_quality": False,
                "enable_candidate_ranking": False,
                "candidate_count": 1,
                "enable_preview_qa": False,
                "enable_preview_auto_fix": False
            },
            "fonts": {
                "preset": "modern",  # Font preset name
                "heading_font": "Montserrat",
                "body_font": "Open Sans"
            },
            "template": {
                "selected": "executive_blue"
            },
            "ui": {
                "theme": "dark",
                "window_width": 1400,
                "window_height": 900
            },
            "paths": {
                "output_folder": "",
                "last_opened": ""
            },
            "wizard_preferences": {
                "audience_index": 0,
                "tone_index": 0,
                "style_id": 2
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get nested config value using dot notation.
        Prioritizes environment variables for API keys.
        """
        # Env Priority for API Keys
        if key == "api.gemini_key" and os.getenv("GEMINI_API_KEY"):
            return os.getenv("GEMINI_API_KEY")
        if key == "api.gemini_keys" and os.getenv("GEMINI_API_KEYS"):
            # Expecting comma separated keys
            return [k.strip() for k in os.getenv("GEMINI_API_KEYS").split(",")]

        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set nested config value using dot notation.
        
        Example: config.set("api.gemini_key", "your-key")
        """
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self._save()
    
    def get_all(self) -> dict:
        """Get entire config dictionary."""
        return self._config.copy()
    
    def reload(self) -> None:
        """Reload config from file."""
        self._load()
