# Phase 01: Customization Dialog UI

**Status:** ⬜ Pending

## Objective

Create the `WizardDialog` to collect user preferences.

## Requirements

- [ ] Create `src/ui/dialogs/wizard_dialog.py`
- [ ] UI Groups:
  - **Audience:** ComboBox [General, Executives, Technical, Clients]
  - **Tone:** ComboBox [Professional, Creative, Minimalist]
  - **Visual Style:** Slider or Radio [Visual Heavy <-> Text Heavy]
- [ ] Return a dictionary of settings on accept.

## Files to Create

- `src/ui/dialogs/wizard_dialog.py`

## Usage

```python
dialog = WizardDialog(parent=self)
if dialog.exec():
    preferences = dialog.get_data()
    # {'audience': 'Technical', 'tone': 'Professional', ...}
```
