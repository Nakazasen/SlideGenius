# Phase 02: AI Integration

## Objective

Teach Gemini to recognize when a requested slide requires a diagram and generating the appropriate structured data.

## Requirements

### Functional

- [x] Update System Prompt in `src/core/ai_service.py` to define "Diagram Schemas".
- [x] Define JSON structure for "Process" (steps) and "Comparison" (left/right).
- [x] Parse AI response and populate `SlideItem.diagram`.

## Implementation Steps

1. [x] Update Prompt: Add instructions for `slide_type="diagram"` and JSON format.
2. [x] Add `draw_comparison` method to `DiagramDrawer`.
3. [x] Update `PPTXGenerator` to route `comparison` type to the new method.
4. [x] Verify: `test_comparison_diagram.pptx` generated with Before/After layout.

## Verified

- `tests/test_diagram.py` now generates `test_comparison_diagram.pptx` with a full Before/After layout matching user's requirement (Translation Process Improvement).
