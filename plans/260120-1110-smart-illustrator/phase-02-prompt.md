# Phase 02: Prompt Engineering

## Objective

Update the main Text AI (Gemini) to generate rich, descriptive image prompts suitable for Imagen.

## Requirements

### Functional

- [x] Update `src/core/ai_service.py` system prompt.
- [x] Instruct AI to populate `image_prompt` field in JSON.
- [x] Format: "Photorealistic style, high quality..." prefixes.

## Implementation Steps

1. [x] Modify System Prompt: Added instruction #5 "HÌNH ẢNH (Smart Illustrator)" and included `image_prompt` in JSON example.
2. [x] Test: Verified prompt structure update.

## Files Modified

- `src/core/ai_service.py`
