# Phase 01: Core Implementation

Status: ✅ Complete

## Objective

Implement the `ModelCascade` class in `src/core/ai_service.py` (or new file) to handle the Waterfall Strategy for model selection and fallback.

## Requirements

### Functional

- [x] Define `ModelConfig` dataclass (id, timeout, active status).
- [x] Implement `ModelCascade` class to manage list of models.
- [x] Implement `generate_content_with_fallback` method.
- [x] Integrate 16 confirmed models into the default configuration.
- [x] Update `AIService` to use `ModelCascade`.

### Non-Functional

- [x] Error handling: Catch timeouts and API errors specifically to trigger fallback.
- [x] Logging: Log which model is being used and when fallback happens.

## Implementation Steps

1. [x] Create `src/core/model_cascade.py` with `ModelCascade` class.
2. [x] Define the confirmed model list in `src/data/defaults.py` or directly in cascade.
3. [x] Implement `execute_waterfall` logic with timeout handling.
4. [x] Refactor `src/core/ai_service.py` to use `ModelCascade`.

## Files to Create/Modify

- `src/core/model_cascade.py` - [NEW] Waterfall logic
- `src/core/ai_service.py` - [MODIFY] Integrate cascade
- `src/data/defaults.py` - [NEW] Default model list (optional)

## Test Criteria

- [x] Test with invalid API key for top model -> Should try next model.
- [x] Test with timeout (simulated) -> Should try next model.
- [x] Test success on first model -> Should return immediately.

## Notes

- Needs `google.api_core.exceptions.DeadlineExceeded` for timeout handling.
- Verify `google-generativeai` version supports all new models (some are preview).

---
Next Phase: phase-02-ui.md
