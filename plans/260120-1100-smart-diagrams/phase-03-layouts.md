# Phase 03: Advanced Layouts

## Objective

Implement complex layouts, specifically the "Before/After" comparison chart and "Decision Tree" logic.

## Requirements

### Functional

- [x] Implement `draw_comparison_diagram()`: Left panel (Before) vs Right panel (After).
- [x] Support different shape colors (Red for "Problem", Green for "Solution").
- [x] Add center arrow between columns.

## Implementation Steps

1. [x] Enhance `DiagramDrawer` with specific layout algorithms (dynamic node height).
2. [x] Add style mapping (colors based on semantic meaning like 'error'/'success').
3. [x] Final Polish: Ensure text doesn't overflow shapes with auto-sizing.

## Verified

- `tests/test_diagram.py` generates `test_comparison_diagram.pptx` with:
  - Center arrow separator.
  - Dynamic node heights based on content count.
  - Polish styling for benefits section.
