# Phase 01: Pollinations Integration

**Status:** ⬜ Pending
**Dependencies:** None (Simple Feature)

## Objective

Update `ImageGenerator` to call Pollinations.ai API as PRIMARY source (before trying paid Imagen).

## Requirements

### Functional

- [ ] Add Pollinations.ai URL builder.
- [ ] Download image via `requests.get()`.
- [ ] Save to `assets/generated_images/`.
- [ ] Keep placeholder as LAST fallback.

### Non-Functional

- [ ] Timeout: 15 seconds per image.
- [ ] Retry: 1 time on failure.

## Implementation Steps

1. [ ] Update `generate_image()` in `src/core/image_generator.py`.
2. [ ] Add `_generate_via_pollinations()` method.
3. [ ] URL Format: `https://image.pollinations.ai/prompt/{encoded_prompt}?width=1920&height=1080&nologo=true`.

## Files to Modify

- `src/core/image_generator.py`

## Test Criteria

- [ ] `tests/test_imagen.py` generates REAL image (not placeholder).
- [ ] Image is high-quality (1920x1080).

---
Next Phase: phase-02-verification.md
