# Phase 01: Template Button Selection UI

**Status:** ✅ Complete

## Completed

- [x] Made template buttons checkable (`setCheckable(True)`)
- [x] Added `:checked` CSS style with background highlight
- [x] Show status bar message: "✅ Đã chọn mẫu: [name]"
- [x] Save selected template to config
- [x] Import test passed

## Changes Made

- Updated `_create_template_btn()` with template_id parameter
- Added `_on_template_selected()` handler
- Added `_update_template_selection()` for visual state
- Template buttons now highlight when selected
