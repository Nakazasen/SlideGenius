# Phase 01: Image Service Core

## Objective

Build the `ImageGenerator` service that connects to Google's Imagen model and handles image retrieval/saving.

## Requirements

### Functional

- [x] Create `src/core/image_generator.py`.
- [x] Implement `generate_image(prompt, output_path)` method.
- [x] Handle API authentication (reuse existing keys) via REST API.
- [x] Create verification script `tests/test_imagen.py`.

## Implementation Steps

1. [x] Research: Used REST API `v1beta/models/...:predict` as SDK support is limited.
2. [x] Implementation: Built class with REST API calls + PIL Fallback.
3. [x] Verification: Confirmed Placeholder generation works when API quota/billing is missing.

## Notes

- **Important:** Current API keys return `400 Billed Expected` or `404 Not Found`.
- **Fallback:** System now defaults to generating a "Placeholder Image" (Blue/Slate background with prompt text) so development can continue.
