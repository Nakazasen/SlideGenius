# Phase 03: Update AI Service Prompt

**Status:** ⬜ Pending
**Dependencies:** Phase 02

## Objective

Teach the AI to use the new context data.

## Tasks

- [ ] Update `AIService.generate_outline(..., context={})`
- [ ] Refactor System Prompt to include:
  - `AUDIENCE_GUIDE`: How to write for specific audiences
  - `TONE_GUIDE`: Vocabulary choice
  - `LAYOUT_GUIDE`: Preference for diagrams vs text

## Files to Modify

- `src/core/ai_service.py`
