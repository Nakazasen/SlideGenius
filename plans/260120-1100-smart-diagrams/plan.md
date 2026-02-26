# Plan: Smart Diagrams (AI-Generated Visuals)

## Goal

Enable SlideGenius to generate actual visual diagrams (shapes, connectors, flows) in PowerPoint, not just text bullets. The AI will determine the structure, and the Python engine will draw it.

## Key Features

- **Smart Layouts:** Automatically draw "Process Flow", "Before/After Comparison", and "Hierarchy" diagrams.
- **AI-Driven Structure:** Gemini returns JSON defining nodes, steps, and relationships.
- **Native PPTX Shapes:** Uses real PowerPoint shapes (editable), not images.

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Drawing Engine Core | ✅ Complete | 100% |
| 02 | AI Integration | ✅ Complete | 100% |
| 03 | Advanced Layouts | ✅ Complete | 100% |

## Tech Stack

- **Backend:** `python-pptx` (Shapes, Connectors, AutoShapes).
- **AI:** Gemini 1.5 Flash (Structured JSON for diagrams).
- **Data:** Extended `SlideItem` model.

## All Phases Complete! 🎉
