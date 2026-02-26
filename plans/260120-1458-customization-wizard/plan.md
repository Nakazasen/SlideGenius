# Plan: Advanced Customization Wizard

**Created:** 2026-01-20T14:58
**Status:** 🟡 In Progress

## Overview

Implement a "Customization Wizard" dialog that intercepts the "Create Outline" action. It collects detailed user preferences to guide the AI, resulting in more targeted and higher-quality slides.

## Goals

- **Contextual Refinement:** Capture Audience, Tone, and Purpose.
- **Visual Guidance:** Capture Layout preferences (Visual vs Text-heavy, Diagram heavy).
- **Better AI Prompts:** Inject these details into the Gemini System Prompt.

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Customization Dialog UI | ⬜ Pending | 0% |
| 02 | Integrate Wizard into App Flow | ⬜ Pending | 0% |
| 03 | Update AI Service Prompt | ⬜ Pending | 0% |

## Detailed Specs

### Phase 1: Customization Dialog UI

Create `src/ui/dialogs/wizard_dialog.py`:

- **Step 1: Context**
  - Target Audience: [Executives, Technical Team, General Clients, Students]
  - Presentation Tone: [Professional, Inspiring, Casual/Fun, Academic]
- **Step 2: Visuals**
  - Detail Level: [High Level (Visuals), Balanced, Detailed (Report)]
  - Language: [Vietnamese, English, Japanese] (Move language here?)
- **Style:** Modern, wizard-like with "Next" or simple single-form. Let's do a single clean form for speed.

### Phase 2: Intercept Flow

- Modify `InputPanel` -> emit `customize_clicked` instead of direct generate?
- Or modify `App._on_generate` to:
    1. Hide InputPanel loading
    2. Show `WizardDialog`
    3. If OK -> Proceed with generation using `(prompt, num_slides, **wizard_data)`

### Phase 3: AI Prompt Engineering

- Update `AIService.generate_outline` signature to accept `context`.
- Construct a rich System Prompt:

    ```
    Target Audience: {audience}
    Tone: {tone}
    Detail Level: {detail_level}
    ```

## Quick Commands

- Start Phase 1: `/code phase-01`
