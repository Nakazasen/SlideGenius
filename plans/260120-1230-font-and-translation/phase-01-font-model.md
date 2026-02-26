# Phase 01: Font Data Model

**Status:** ✅ Complete

## Objective

Define font presets and add font configuration to Settings.

## Completed

- [x] Created `FontPreset` dataclass in `models.py`
- [x] Added `FONT_PRESETS` with 10 font pairs
- [x] Added `get_font_preset()` helper function
- [x] Added `fonts` section to `ConfigManager` defaults

## Font Presets

| Name | Heading | Body |
|------|---------|------|
| Modern | Montserrat | Open Sans |
| Classic | Georgia | Times New Roman |
| Clean | Helvetica | Arial |
| Tech | Roboto | Roboto Mono |
| Elegant | Playfair Display | Lato |
| Minimal | Inter | Inter |
| Bold | Impact | Arial |
| Friendly | Poppins | Nunito |
| Corporate | Calibri | Calibri Light |
| Creative | Raleway | Source Sans Pro |
