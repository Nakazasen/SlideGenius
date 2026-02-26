# Phase 02: Integrate Wizard into App Flow

**Status:** ⬜ Pending
**Dependencies:** Phase 01

## Objective

Connect the "Create Outline" button to the Wizard Dialog instead of triggering generation immediately.

## Tasks

- [ ] Modify `src/app.py`: `_on_generate`
- [ ] Update `generate_clicked` signal signature in `InputPanel` (optional, or just pass prompt)
- [ ] Logic:
  - User clicks "Create Outline" -> `InputPanel` emits signal
  - `App` receives signal
  - `App` opens `WizardDialog`
  - If User cancels -> Stop
  - If User OKs -> Call `Worker` with new params

## Files to Modify

- `src/app.py`
