# SlideGenius - AI Slide Generator

## Project Overview

SlideGenius is a Windows desktop application for generating PowerPoint presentations using AI. Built with PySide6 (Qt 6) and Google Gemini API.

## Quick Start

```bash
cd c:\ProgramData\Sandbox\SlideGenius
pip install -r requirements.txt
python main.py
```

## Architecture

- **Entry Point**: `main.py` → `src/app.py` (SlideGeniusApp)
- **UI Framework**: PySide6 with Dark/Light theming via QSS
- **AI Engine**: Google Gemini 1.5 Flash for outline generation
- **PPTX Generation**: python-pptx library
- **Database**: SQLite for history storage

## Key Files

| File | Purpose |
|------|---------|
| `src/app.py` | Main window with 3-column layout |
| `src/core/ai_service.py` | Gemini API integration |
| `src/core/pptx_generator.py` | PowerPoint file generation |
| `src/data/models.py` | Data models (Outline, SlideItem, Template) |
| `src/ui/theme_manager.py` | Dark/Light mode switching |

## Features Implemented

- ✅ AI Outline Generation (Gemini)
- ✅ PPTX Export with 5 templates
- ✅ Dark/Light mode
- ✅ Settings dialog for API configuration
- ✅ History database

## Status

**MVP Complete** - All 6 phases finished on 2026-01-20.

## Development Notes

- API key required: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Templates: modern_blue, creative_orange, minimal_gray, nature_green, purple_gradient
- Warning: google.generativeai package deprecated but functional

## Next Steps (Optional)

1. Test with real API key
2. Implement template selection in UI
3. Add History view tab
4. Migrate to google.genai package
