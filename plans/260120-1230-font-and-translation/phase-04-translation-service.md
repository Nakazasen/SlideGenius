# Phase 04: Translation Service

**Status:** ✅ Complete

## Completed

- [x] Created `src/core/translation_service.py`
- [x] Supports VI ↔ EN, VI ↔ JP, EN ↔ JP
- [x] `translate_outline()` - translate full or selected slides
- [x] `_translate_slide()` - translate single slide via Gemini
- [x] `get_language_pairs()` - UI helper for dropdowns
- [x] Import test passed

## API Design

```python
service = TranslationService()
translated = service.translate_outline(
    outline=original_outline,
    target_lang="en",  # "vi", "en", "ja"
    slide_indices=[0, 2, 4]  # Optional: None = all
)
```
