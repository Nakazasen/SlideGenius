# SlideGenius Architecture

Last updated: 2026-06-19 for local branch `chore/merge-stabilize-export-pipeline`, commit `995b3df79d1b5b1d450ffc60ee6adc06fa7e62be`.

## Runtime overview

SlideGenius is a Windows desktop application built with PySide6. The merged runtime is organized around this flow:

```text
User prompt / settings
  -> GenerateWorker
  -> AIService
      -> ConfigManager
      -> ModelCascade
      -> StorylineEngine
      -> optional PreviewQAGate
  -> Outline / SlideItem schema v2
  -> presentation_spec normalization and layout budgets
  -> PPTXGenerator + DiagramDrawer
  -> editable .pptx
```

Preview QA, when enabled and available, adds an optional rendered-preview loop:

```text
Outline
  -> temporary PPTX render
  -> PowerPoint COM export to PNG
  -> OpenCV/PIL density and clipping heuristics
  -> optional deterministic remediation variant
  -> QA metadata on Outline/SlideItem
```

## Core components

### UI and worker layer

- `main.py` launches the app.
- `src/app.py` owns the main desktop window and UI wiring.
- `src/ui/workers.py` runs generation in a `QThread`, sets interactive/stable defaults, emits progress, and optionally dispatches parallel image generation when stable mode is disabled.
- `src/ui/dialogs/settings_tabs/ai_tab.py` exposes Gemini API-key list input and waterfall strategy messaging.
- `src/ui/*` contains Qt widgets, dialogs, styles, and theme management.

### Configuration and templates

- `src/data/config_manager.py` reads `config.json`, migrates a single Gemini key to a list, loads API keys from environment variables, and stores generation defaults.
- Current template support in `src/data/templates.py` is a static list of template IDs, colors, and descriptions.
- There is not yet a full template registry with layout capability metadata, budget overrides, or validation.

### AI orchestration

- `src/core/ai_service.py` is the primary entry point for outline generation.
- `AIService` responsibilities:
  - configure Gemini keys through `ModelCascade`;
  - choose stable/interactive path;
  - build the system prompt;
  - generate one or more raw candidates;
  - run `StorylineEngine` rewrite/scoring;
  - select the best candidate;
  - apply optional preview QA.
- `src/core/model_cascade.py` performs the current Gemini waterfall execution.
- `ModelCascade` responsibilities:
  - load active model strategy from config;
  - filter unsupported model tokens such as audio/image/video models;
  - rotate Gemini keys on quota-like errors;
  - try active models sequentially;
  - return the first successful response.
- Current limitation: `ModelCascade` does not yet have typed provider candidates, health state, cooldown deadlines, attempt records, or detailed error taxonomy.

### Storyline and quality layer

- `src/core/storyline_engine.py` performs higher-level presentation planning:
  - candidate strategy voice;
  - optional model rewrite;
  - deterministic local rewrite;
  - duplicate/transition/CTA repair;
  - optional AI self-critique;
  - optional quality retry;
  - visual treatment refinement;
  - QA findings and quality scoring.
- This layer should remain presentation-domain logic and should not own provider routing.

### Semantic presentation model

- `src/data/models.py` defines `Outline`, `SlideItem`, `Template`, `SlideType`, and supported layout variants.
- `Outline` carries quality metadata, candidate metadata, QA findings, and preview-QA status.
- `SlideItem` carries content plus semantic render hints:
  - `layout_variant`;
  - `storyline_role`;
  - `summary`;
  - `key_message`;
  - `stats`;
  - `chart_spec`;
  - `table_spec`;
  - `qa_flags`;
  - `render_warnings`;
  - `preview_density_score`;
  - `remediation_variant`.

### Layout normalization and budget layer

- `src/core/presentation_spec.py` normalizes outlines before export.
- It maps semantic slide content into safe layout budgets.
- It provides content fitting to reduce overflow before PPTX rendering.
- It emits fit warnings and visible/trimmed content state for renderer use.

### PPTX rendering

- `src/core/pptx_generator.py` uses `python-pptx` to generate editable PowerPoint files.
- It maps layout variants to concrete slide rendering methods.
- It uses `fit_slide_content` to avoid uncontrolled overflow.
- `src/core/diagram_drawer.py` draws primitive process and comparison diagrams as editable PowerPoint shapes.
- Export should remain editable; slide flattening should only be used for optional QA previews, not as the main output format.

### Preview QA

- `src/core/preview_qa.py` renders temporary PPTX files to PNG via PowerPoint COM.
- It analyzes rendered images using PIL, NumPy, and OpenCV.
- It detects visual density, crowded lower thirds, edge crowding, and possible clipping.
- It can select a deterministic remediation variant and re-render to score alternatives.
- It must be treated as optional because it depends on Windows + local Microsoft PowerPoint automation.

## Reference architecture findings

### Presenton comparison

Presenton is a larger presentation-generation platform with:

- Docker/Electron deployment options;
- FastAPI backend;
- Next.js UI;
- API-first presentation generation;
- multi-provider LLM and image configuration;
- template and theme support;
- export task services with subprocess isolation, timeouts, output path checks, and logging;
- document ingestion/conversion services;
- image, icon, stock asset, and ComfyUI/OpenAI-compatible provider services;
- background task and observability patterns;
- MCP endpoint support.

SlideGenius should borrow separation of concerns, not the full platform footprint. The most relevant ideas are:

- template registry and validation;
- export task observability;
- provider configuration boundaries;
- document/image/icon/chart services as optional modules;
- explicit asset output paths and fallback behavior;
- structured logs for start/end/failure of export-like tasks.

### translation_app comparison

translation_app has a mature provider-router pattern:

- provider/model/key candidates;
- provider state per provider/model/key;
- health statuses such as `healthy`, `degraded`, `cooldown`, `dead`;
- error classification for auth, quota, timeout, transport, token-limit, model errors, and provider 5xx;
- cooldown and throttle behavior;
- attempt records;
- dynamic provider/model ranking;
- config/secrets boundaries;
- fake-provider tests.

SlideGenius should evolve `ModelCascade` toward a presentation-generation AI Runtime while keeping translation-specific request/result classes out of this codebase.

## Architectural boundaries

```text
Provider routing infrastructure
  Owns: providers, models, keys, attempts, error classes, cooldown, health.
  Must not own: slide schema, storyline roles, layout decisions.

Storyline pipeline
  Owns: narrative quality, candidate strategy, rewrite, QA findings, scoring.
  Must not own: API-key rotation, provider cooldown, renderer internals.

Renderer/export pipeline
  Owns: layout budgets, PPTX shapes, warnings, validation, output files.
  Must not own: provider retry or prompt strategy.
```

## Architectural risks

1. Unit tests currently reach real Gemini APIs in key-rotation/waterfall cases.
2. Preview QA depends on local Microsoft PowerPoint automation.
3. README/GEMINI docs are stale versus the merged schema-v2 pipeline.
4. Current provider waterfall is less observable than translation_app's router.
5. Layout support is richer than the old docs imply, so unsupported variant handling needs strict tests.
6. Template support is still static and lacks a capability matrix.
7. Export warnings are not yet fully covered by golden/offline tests.
8. Image generation exists but should remain optional until export stability and asset caching are stronger.

## Recommended target architecture

```text
UI
  -> GenerationController
      -> AIRuntime
          -> ProviderRouter
          -> GeminiAdapter
          -> future OpenAICompatibleAdapter
      -> StorylinePipeline
      -> QualityGate
      -> ExportService
          -> TemplateRegistry
          -> LayoutBudgetEngine
          -> PPTXRenderer
          -> PPTXValidator
          -> PreviewQAGate optional
```

Key principles:

- Provider routing is infrastructure, not presentation logic.
- Storyline and layout semantics are domain logic.
- Rendering is deterministic and testable offline.
- Preview QA is an optional capability with clear skipped reasons.
- Documentation must reflect code reality after each merge.
- Near-term evolution stays desktop PySide6/Python; no web rewrite is planned.
