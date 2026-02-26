# Phase 03: PPTX Integration

## Objective

Update the PowerPoint generator to fetch images (if prompted) and place them nicely on the slide.

## Requirements

### Functional

- [x] Update `PPTXGenerator` to check for `image_prompt`.
- [x] Call `ImageGenerator` to get the file path.
- [x] Insert image into Layout (Left Content, Right Image).
- [x] Handle layout adjustments (resize/crop).

## Implementation Steps

1. [x] Modify `src/core/pptx_generator.py`: Added logic to `_add_content_slide`.
2. [x] Add logic: If `image_prompt` exists -> Generate Image -> Insert.
3. [x] Optimize layout: Adjusted text box width when image is present.
4. [x] Verification: `test_illustrator.py` successfully generated slide with image.

## Files Modified

- `src/core/pptx_generator.py`
