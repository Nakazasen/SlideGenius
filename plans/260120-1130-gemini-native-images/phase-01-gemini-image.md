# Phase 01: Gemini Image Integration

**Status:** ⬜ Pending
**Dependencies:** None

## Objective

Add `_generate_via_gemini_native()` method to `ImageGenerator` using Google's native image models.

## Requirements

### Functional

- [ ] Implement Gemini Flash Image call (`gemini-2.5-flash-image`)
- [ ] Implement Gemini Pro Image call (`gemini-3-pro-image-preview`)
- [ ] Save generated image to disk

## Implementation Steps

1. [ ] Research: Check `google-genai` SDK syntax for image generation
2. [ ] Add `_generate_via_gemini_native()` method
3. [ ] Handle response parsing (base64 image data)

## Files to Modify

- `src/core/image_generator.py`

## Notes

- SDK method likely: `model.generate_images()` or `model.generate_content()` with image output
- Need to handle new SDK syntax for 2026 models
