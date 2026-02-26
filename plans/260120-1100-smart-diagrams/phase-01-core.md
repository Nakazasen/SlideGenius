# Phase 01: Drawing Engine Core

## Objective

Build the foundational `DiagramDrawer` class capable of rendering basic shapes and connecting them on a slide.

## Requirements

### Functional

- [x] Define `DiagramData` schema in `src/data/models.py`.
- [x] Create `src/core/diagram_drawer.py`.
- [x] Implement `draw_node(x, y, text, style)`: Draw a rectangle/shape with text.
- [x] Implement `draw_connector(shape1, shape2)`: Connect two shapes.
- [x] Integrate into `PPTXGenerator`: Add handling for `slide_type="diagram"`.

## Implementation Steps

1. [x] Update `src/data/models.py` to add `diagram: Optional[Dict]` field to `SlideItem`.
2. [x] Create `src/core/diagram_drawer.py` with `DiagramDrawer` class.
3. [x] Implement logic to draw a simple "Linear Process" (Step 1 -> Step 2 -> Step 3).
4. [x] Create a CLI test script to generate a sample PPTX with a diagram.

## Verified

- `tests/test_diagram.py` generated `test_diagram.pptx` with shapes and text.
