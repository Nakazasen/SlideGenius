import os
import time
from pathlib import Path
from typing import List, Optional
import importlib.util
try:
    # FORCE DISABLE: The import hangs in this environment. 
    # Validated via debugging steps 521-532.
    raise ImportError("Module disabled due to hang")
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

from src.data.config_manager import ConfigManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

import requests
import base64
import json

class ImageGenerator:
    """Service to generate images using multiple AI sources."""
    
    # Priority List of Models
    IMAGE_MODELS = [] # Disabling Google GenAI for images as it requires specific access/billing

    def __init__(self):
        self.config = ConfigManager()
        self.api_keys = self._load_api_keys()
        self.output_dir = Path("assets/generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_api_keys(self) -> List[str]:
        """Load API keys from config."""
        keys = self.config.get("api.gemini_keys", [])
        if not keys:
            single = self.config.get("api.gemini_key", "")
            if single:
                keys = [single]
        return keys

    def generate_image(self, prompt: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Generate an image from prompt and save to disk.
        Priority: 1. Pollinations.ai -> 2. Picsum (Fallback) -> 3. Placeholder
        """
        # Simple timestamp filename if not provided
        if not filename:
            filename = f"gen_{int(time.time())}.png"
        
        output_path = self.output_dir / filename
        
        # === PRIORITY 1: Pollinations.ai (FREE) ===
        # Try multiple times
        for _ in range(2):
            result = self._generate_via_pollinations(prompt, output_path)
            if result:
                return result
            time.sleep(1)
            
        # === PRIORITY 2: Picsum (Reliable Fallback) ===
        result = self._generate_via_picsum(output_path)
        if result:
            return result

        # === PRIORITY 3: Placeholder (Last Resort) ===
        logger.warning("All image generation attempts failed. Using placeholder.")
        return self._generate_placeholder(prompt, output_path)

    def _generate_via_google_genai(self, prompt: str, output_path: Path) -> Optional[str]:
        """Generate image using google-genai SDK (Imagen methods)."""
        for key in self.api_keys:
            client = genai. Client(api_key=key)
            
            for model_name in self.IMAGE_MODELS:
                try:
                    logger.info(f"Attempting Google GenAI: {model_name}")
                    
                    # Method 1: generate_images (Specific to Imagen)
                    if "imagen" in model_name:
                        response = client.models.generate_images(
                            model=model_name,
                            prompt=prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                aspect_ratio="16:9" 
                            )
                        )
                        if response and response.generated_images:
                            image_bytes = response.generated_images[0].image.image_bytes
                            output_path.write_bytes(image_bytes)
                            logger.info(f"Imagen SUCCESS: {output_path}")
                            return str(output_path.absolute())

                    # Method 2: generate_content (Multimodal fallback)
                    else:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=f"Generate a high-quality image: {prompt}",
                            config=types.GenerateContentConfig(
                                response_modalities=["IMAGE"]
                            )
                        )
                        if response and response.candidates:
                            for part in response.candidates[0].content.parts:
                                if part.inline_data:
                                    output_path.write_bytes(part.inline_data.data)
                                    logger.info(f"Gemini Content SUCCESS: {output_path}")
                                    return str(output_path.absolute())
                    
                except Exception as e:
                    logger.warning(f"Google GenAI error ({model_name}): {e}")
                    continue
        
        return None

    def _generate_via_pollinations(self, prompt: str, output_path: Path) -> Optional[str]:
        """Generate image using Pollinations.ai."""
        try:
            # Simple URL encoding manually or rely on requests
            # Pollinations format: https://image.pollinations.ai/prompt/{prompt}
            base_url = "https://image.pollinations.ai/prompt/"
            params = {
                "width": 1920,
                "height": 1080,
                "nologo": "true",
                "seed": int(time.time()) # Random seed
            }
            
            # Construct URL carefully with encoding
            import urllib.parse
            safe_prompt = urllib.parse.quote(prompt)
            final_url = f"{base_url}{safe_prompt}" 
            
            logger.info(f"Pollinations.ai attempting: {final_url[:50]}...")
            
            response = requests.get(final_url, params=params, timeout=30)
            
            if response.status_code == 200 and len(response.content) > 1000:
                output_path.write_bytes(response.content)
                logger.info(f"Pollinations.ai SUCCESS: {output_path}")
                return str(output_path.absolute())
            else:
                logger.warning(f"Pollinations.ai failed status: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Pollinations.ai error: {e}")
        
        return None

    def _generate_via_picsum(self, output_path: Path) -> Optional[str]:
        """Generate a random nice image from Picsum."""
        try:
            # 1920x1080 random image
            # Add random seed to avoid caching
            seed = int(time.time())
            url = f"https://picsum.photos/seed/{seed}/1920/1080"
            
            logger.info("Attempting Picsum fallback...")
            response = requests.get(url, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                output_path.write_bytes(response.content)
                logger.info(f"Picsum SUCCESS: {output_path}")
                return str(output_path.absolute())
                
        except Exception as e:
            logger.warning(f"Picsum error: {e}")
            
        return None

    def _generate_placeholder(self, prompt: str, output_path: Path) -> str:
        """Generate a placeholder image locally using PIL."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            width, height = 1920, 1080 
            img = Image.new('RGB', (width, height), color='#1e293b') # Slate-800
            draw = ImageDraw.Draw(img)
            
            # Border
            draw.rectangle([10, 10, width-10, height-10], outline='#ef4444', width=5) # Red for error
            
            # Text
            text = f"IMAGE GENERATION FAILED\n\nPrompt: {prompt[:50]}..."
            
            try:
                font = ImageFont.load_default()
                # Scale up default font not easy, just use it
            except:
                pass

            draw.text((width//2, height//2), text, fill="white", anchor="mm")
            
            img.save(output_path)
            return str(output_path.absolute())
            
        except Exception as e:
            logger.error(f"Placeholder gen failed: {e}")
            return str(output_path) # Should act as path str
