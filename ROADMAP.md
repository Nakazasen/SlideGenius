# SlideGenius Roadmap

Last updated: 2026-06-19 after auditing local branch `chore/merge-stabilize-export-pipeline` at commit `995b3df79d1b5b1d450ffc60ee6adc06fa7e62be`.

## Current baseline

SlideGenius is no longer only an MVP outline-to-PPTX tool. The merged local code adds a more serious export pipeline:

- Semantic schema v2 in `src/data/models.py` with layout variants, story roles, QA fields, render warnings, and preview QA metadata.
- `AIService` in `src/core/ai_service.py` as the generation entry point, wiring config, model cascade, storyline rewrite, stable mode, candidate selection, and optional preview QA.
- Storyline orchestration in `src/core/storyline_engine.py` for candidate strategy, local rewrite, optional AI critique, quality scoring, QA findings, visual treatment, and low-quality retry.
- Model waterfall in `src/core/model_cascade.py` with Gemini API-key rotation, text-model filtering, and sequential fallback.
- Layout budget and semantic normalization in `src/core/presentation_spec.py`.
- Native editable PPTX rendering in `src/core/pptx_generator.py` plus primitive diagram support in `src/core/diagram_drawer.py`.
- Preview image QA in `src/core/preview_qa.py`, using PowerPoint COM + OpenCV heuristics when enabled and available.
- Current template support is still a small static list in `src/data/templates.py`, not a full registry/capability matrix.

## Audit inputs

- Local source of truth: `D:\Sandbox\SlideGenius`.
- Local working branch: `chore/merge-stabilize-export-pipeline`.
- Commit analyzed: `995b3df79d1b5b1d450ffc60ee6adc06fa7e62be`.
- Merged source branch: `origin/codex/stabilize-export-pipeline`.
- Remote origin: `https://github.com/Nakazasen/SlideGenius.git`.
- Presenton reference: `D:\Sandbox\reference_repos\presenton`.
- translation_app reference: `D:\Sandbox\reference_repos\translation_app`.

> [!IMPORTANT]
> This roadmap describes the local branch after merge. It does not claim that remote `main` has been pushed or updated.

## Verification snapshot

- `py --version`: Python 3.13.5.
- `py -m pytest`: passes by default after SG-001/SG-002 test isolation and SG-003 export coverage.
- Latest full run: 50 passed, 4 skipped.
- Live provider/model scans and manual OS-open checks are marked as integration/live-provider checks and skipped by default.
- Core import smoke check: passed.
- Scripted PPTX smoke export: `scripts/generate_workshop_psychological_safety.py` generated an 11-slide editable PPTX.
- SG-003 added offline golden export tests in `tests/test_export_layouts.py` for editable PPTX export, native chart/table/diagram scenarios, dense content warning/review banner behavior, and unsupported layout fallback warnings.
- Next recommended issue: SG-004 PresentationSpec/schema contract tests, followed by SG-005 PPTX validator/export warnings.

## Priority 0 — Stabilize testability and CI

1. Isolate AI tests from live Gemini calls.
   - Mock `google.genai.Client` and any remaining legacy `google.generativeai` paths.
   - Add a no-network default for unit tests.
   - Move live provider checks behind explicit integration markers.
   - Add fake provider/client tests for success, auth failure, quota, timeout, model unavailable, and provider 5xx.
2. Add deterministic export regression tests.
   - Build representative outlines for each layout variant.
   - Assert slide count, non-empty shapes, warnings, and no render exceptions.
   - Include `PresentationSpec` contract tests for schema normalization and layout budgets.
3. Add a documented smoke command sequence.
   - Dependency install.
   - Offline unit test suite.
   - Core import smoke.
   - Offline PPTX export smoke.

## Priority 1 — Productionize AI Runtime

SlideGenius currently has a Gemini waterfall, but translation_app shows a more robust provider-router model. Adopt the pattern, not the translation domain objects.

1. Define a SlideGenius AI Runtime contract.
   - `GenerationRequest` for deck/storyline tasks, not translation requests.
   - `GenerationResult` carrying text/JSON response, provider metadata, and attempts.
   - `ProviderCandidate` for provider/model/key combinations.
2. Introduce provider state tracking.
   - Provider/model/key identity.
   - Success/failure counts.
   - Last latency.
   - Last error class.
   - Cooldown deadline.
   - Health status such as healthy, degraded, cooldown, dead.
3. Classify errors consistently.
   - Auth failure.
   - Quota/rate limit.
   - Token/context limit.
   - Timeout/transport.
   - Model unavailable.
   - Provider 5xx.
4. Make routing observable.
   - Store attempt records on generated outlines or generation metadata.
   - Show selected model, fallback count, and failure reasons in UI/logs.
   - Never log raw API keys.
5. Support BYOK expansion without destabilizing current Gemini behavior.
   - Gemini remains default.
   - Add an OpenAI-compatible adapter only after contract and fake-provider tests exist.
   - Keep provider router independent from slide/storyline code.

## Priority 2 — Template and rendering architecture

Presenton demonstrates strong separation between API, templates, export tasks, image generation, assets, and presentation memory. SlideGenius should evolve these boundaries inside the existing desktop PySide6/Python stack.

1. Create a template registry.
   - Theme tokens.
   - Font tokens.
   - Layout capabilities.
   - Variant support matrix.
   - Safe content budgets per template.
2. Add template validation.
   - Verify required colors/fonts.
   - Verify each layout has render support.
   - Fail visibly or warn explicitly on unknown layout variants.
3. Strengthen chart/table/diagram rendering.
   - More test fixtures for dense data.
   - Graceful fallback from chart/table layouts to content summaries.
   - Explicit render warnings for unsupported or trimmed data.
4. Add export task observability inspired by Presenton.
   - Export start/end events.
   - Output path and size.
   - Slide count.
   - Warning counts.
   - Runtime capability notes such as preview QA skipped.
5. Keep exported PPTX fully editable.
   - Avoid flattening slides to images except for optional previews.

## Priority 3 — Preview QA and auto-remediation

1. Make preview QA optional and capability-aware.
   - PowerPoint COM is Windows/Office-dependent.
   - Detect missing PowerPoint and report a clear skipped reason.
2. Persist preview QA reports.
   - Per-slide density score.
   - Flags.
   - Chosen remediation variant.
   - Before/after candidate score.
3. Expand remediation beyond a single pass.
   - Candidate variants by layout family.
   - Tie-break on story-role alignment.
   - Never silently discard important content without a note.

## Priority 4 — Document, asset, and image pipeline

Borrow Presenton's modular service boundaries without copying its platform architecture.

1. Document input should be staged and measured.
   - Plain text and markdown first.
   - DOCX/PDF only with fixtures and clear fidelity notes.
   - Website links only after grounding and citation strategy are defined.
2. Image/icon handling should be optional and cache-aware.
   - Keep generation disabled in stable mode by default.
   - Cache generated assets by prompt/model where practical.
   - Degrade gracefully to editable text/layout when image providers fail.
3. Chart/icon/data rendering should stay native/editable where possible.
   - Prefer PowerPoint shapes/charts/tables over rasterized slide content.

## Priority 5 — User-facing generation workflow

1. UI should expose the new pipeline truthfully.
   - Candidate strategy.
   - Quality summary.
   - Preview QA applied/skipped.
   - Render warnings.
   - Provider/model attempts after AI Runtime exists.
2. Settings should distinguish stable/offline-safe behavior from live-provider checks.
3. User-facing copy should be localized and concise, with no leaked provider secrets.

## Priority 6 — Packaging and release hygiene

1. Update README and quickstart paths to the real local/dev expectations.
2. Keep `CHANGELOG.md` entries per merge/release.
3. Keep `AGENT_RULES.md` as the operating contract for future coding agents.
4. Add release checklist:
   - Clean git status.
   - Tests pass or known failures documented.
   - PPTX smoke export passes.
   - Manual launch tested on Windows.

## Non-goals for the next milestone

- Do not rewrite the app as a web service.
- Do not copy Presenton's full FastAPI/Next/Electron architecture.
- Do not copy translation_app's translation request/result domain objects.
- Do not add many providers before the Gemini route is fully testable.
- Do not claim PDF/DOCX import fidelity until measured with fixtures.
- Do not claim remote `main` is updated unless push/remote verification is done.
