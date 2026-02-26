"""Translation Service - Translate slide content using Gemini with Google Translate backup."""
import json
from typing import List, Optional
from src.data.models import Outline, SlideItem
from src.data.config_manager import ConfigManager
from src.core.model_cascade import ModelCascade
from src.utils.logger import get_logger
from google.genai import types

logger = get_logger(__name__)


class TranslationService:
    """Service to translate presentation outlines using Gemini + Google Translate fallback."""
    
    SUPPORTED_LANGUAGES = {
        "vi": "Vietnamese",
        "en": "English", 
        "ja": "Japanese"
    }
    
    # Language codes for deep-translator
    LANG_CODES = {
        "vi": "vi",
        "en": "en", 
        "ja": "ja"
    }
    
    def __init__(self):
        self.config = ConfigManager()
        self.cascade = ModelCascade()
        self._configure_api()
    
    def _configure_api(self) -> None:
        """Configure Gemini API."""
        api_keys = self.config.get("api.gemini_keys", [])
        if not api_keys:
            single = self.config.get("api.gemini_key", "")
            if single:
                api_keys = [single]
        self.cascade.configure_api(api_keys)
    
    def translate_outline(
        self, 
        outline: Outline, 
        target_lang: str,
        slide_indices: Optional[List[int]] = None
    ) -> Outline:
        """
        Translate an outline to a target language.
        
        Args:
            outline: The source Outline object
            target_lang: Target language code ("en", "vi", "ja")
            slide_indices: Optional list of slide indices to translate. 
                           If None, translates all slides.
        
        Returns:
            A new Outline object with translated content
        """
        if target_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {target_lang}")
        
        source_lang = outline.language or "vi"
        target_lang_name = self.SUPPORTED_LANGUAGES[target_lang]
        source_lang_name = self.SUPPORTED_LANGUAGES.get(source_lang, "Vietnamese")
        
        # Determine which slides to translate
        if slide_indices is None:
            slides_to_translate = list(range(len(outline.slides)))
        else:
            slides_to_translate = [i for i in slide_indices if 0 <= i < len(outline.slides)]
        
        # Create a copy of the outline
        translated_slides = []
        
        for i, slide in enumerate(outline.slides):
            if i in slides_to_translate:
                translated_slide = self._translate_slide(slide, source_lang, target_lang, source_lang_name, target_lang_name)
                translated_slides.append(translated_slide)
            else:
                translated_slides.append(slide)
        
        # Translate title
        translated_title = self._translate_text(outline.title, source_lang, target_lang, source_lang_name, target_lang_name)
        
        return Outline(
            title=translated_title,
            slides=translated_slides,
            language=target_lang
        )
    
    def _translate_slide(self, slide: SlideItem, source_code: str, target_code: str, 
                         source_lang: str, target_lang: str) -> SlideItem:
        """Translate a single slide using Gemini, fallback to Google Translate."""
        
        # Try Gemini first
        translated = self._translate_slide_gemini(slide, source_lang, target_lang)
        if translated:
            logger.info(f"Slide translated via Gemini: {slide.title[:30]}")
            return translated
        
        # Fallback to Google Translate
        logger.warning("Gemini translation failed, falling back to Google Translate")
        return self._translate_slide_google(slide, source_code, target_code)
    
    def _translate_slide_gemini(self, slide: SlideItem, source_lang: str, target_lang: str) -> Optional[SlideItem]:
        """Translate slide using Gemini AI."""
        content_to_translate = {
            "title": slide.title,
            "content": slide.content,
            "speaker_notes": slide.speaker_notes
        }
        
        prompt = f'''Translate the following slide content from {source_lang} to {target_lang}.
Keep the exact same JSON structure. Only translate the text values.
Do NOT translate technical terms, proper nouns, or brand names.
Return ONLY valid JSON, no markdown code blocks.

Input:
{json.dumps(content_to_translate, ensure_ascii=False, indent=2)}

Output (translated to {target_lang}):'''
        
        try:
            response = self.cascade.generate_content(
                prompt,
                generation_config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            translated_data = json.loads(response.text)
            
            return SlideItem(
                title=translated_data.get("title", slide.title),
                content=translated_data.get("content", slide.content),
                slide_type=slide.slide_type,
                speaker_notes=translated_data.get("speaker_notes", slide.speaker_notes),
                image_prompt=slide.image_prompt,
                diagram=slide.diagram
            )
            
        except Exception as e:
            logger.error(f"Gemini translation failed: {e}")
            return None
    
    def _translate_slide_google(self, slide: SlideItem, source_code: str, target_code: str) -> SlideItem:
        """Translate slide using Google Translate (deep-translator)."""
        try:
            from deep_translator import GoogleTranslator
            
            translator = GoogleTranslator(source=source_code, target=target_code)
            
            # Translate title
            translated_title = translator.translate(slide.title) if slide.title else slide.title
            
            # Translate content list
            translated_content = []
            for item in slide.content:
                if item:
                    translated_content.append(translator.translate(item))
                else:
                    translated_content.append(item)
            
            # Translate speaker notes
            translated_notes = translator.translate(slide.speaker_notes) if slide.speaker_notes else ""
            
            logger.info(f"Slide translated via Google Translate: {slide.title[:30]}")
            
            return SlideItem(
                title=translated_title,
                content=translated_content,
                slide_type=slide.slide_type,
                speaker_notes=translated_notes,
                image_prompt=slide.image_prompt,
                diagram=slide.diagram
            )
            
        except Exception as e:
            logger.error(f"Google Translate failed: {e}")
            return slide  # Return original if all fails
    
    def _translate_text(self, text: str, source_code: str, target_code: str,
                        source_lang: str, target_lang: str) -> str:
        """Translate text using Gemini, fallback to Google Translate."""
        if not text:
            return text
        
        # Try Gemini first
        translated = self._translate_text_gemini(text, source_lang, target_lang)
        if translated:
            return translated
        
        # Fallback to Google Translate
        return self._translate_text_google(text, source_code, target_code)
    
    def _translate_text_gemini(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate text using Gemini AI."""
        prompt = f'''Translate the following text from {source_lang} to {target_lang}.
Return ONLY the translated text, nothing else.

Text: {text}

Translation:'''
        
        try:
            response = self.cascade.generate_content(
                prompt,
                generation_config=types.GenerateContentConfig(
                    temperature=0.3
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini text translation failed: {e}")
            return None
    
    def _translate_text_google(self, text: str, source_code: str, target_code: str) -> str:
        """Translate text using Google Translate."""
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source=source_code, target=target_code)
            return translator.translate(text)
        except Exception as e:
            logger.error(f"Google Translate text failed: {e}")
            return text
    
    def get_language_pairs(self) -> List[tuple]:
        """Get available translation pairs for UI."""
        return [
            ("vi", "en", "🇻🇳 Việt → 🇺🇸 Anh"),
            ("en", "vi", "🇺🇸 Anh → 🇻🇳 Việt"),
            ("vi", "ja", "🇻🇳 Việt → 🇯🇵 Nhật"),
            ("ja", "vi", "🇯🇵 Nhật → 🇻🇳 Việt"),
            ("en", "ja", "🇺🇸 Anh → 🇯🇵 Nhật"),
            ("ja", "en", "🇯🇵 Nhật → 🇺🇸 Anh"),
        ]
