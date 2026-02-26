# Phase 02: UI Configuration

Status: ✅ Complete
Dependencies: phase-01-core.md

## Objective

Update the Settings Dialog to allow viewing and (optionally) toggling models in the waterfall strategy.

## Requirements

### Functional

- [x] Add "Waterfall Strategy" tab or section in Settings.
- [x] Display list of models with their status (Active/Inactive).
- [x] Allow simple enable/disable of models (saved to config).
- [x] (Optional) Reorder models.

## Implementation Steps

1. [x] Update `config.json` schema to store `waterfall_strategy` override.
2. [x] Modify `src/ui/dialogs/settings_dialog.py` to add new tab.
3. [x] Create `ModelListComponent` to render the list.
4. [x] Bind save logic to `ConfigManager`.

## Files to Create/Modify

- `src/ui/dialogs/settings_dialog.py` - [MODIFY] Add tab
- `src/data/config_manager.py` - [MODIFY] Handle list config

## Test Criteria

- [x] Can toggle a model off -> It is skipped in waterfall.
- [x] API Key change still works.

---
Next Phase: phase-03-test.md
