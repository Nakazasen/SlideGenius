# Changelog

All notable changes to SlideGenius will be documented in this file.

## Unreleased

### Merge and audit

- Merged `origin/codex/stabilize-export-pipeline` into local branch `chore/merge-stabilize-export-pipeline`.
- Audited the merged local code at `D:\Sandbox\SlideGenius`.
- Audited reference repositories:
  - Presenton at `D:\Sandbox\reference_repos\presenton`.
  - translation_app at `D:\Sandbox\reference_repos\translation_app`.
- Added project documentation at the repository root:
  - `ROADMAP.md`.
  - `ARCHITECTURE.md`.
  - `AGENT_RULES.md`.
  - `CHANGELOG.md`.
- Re-audited the root docs against local branch `chore/merge-stabilize-export-pipeline`, commit `995b3df79d1b5b1d450ffc60ee6adc06fa7e62be`.

### Current technical baseline

- `AIService` wires config, Gemini waterfall, storyline processing, candidate selection, stable mode, and optional preview QA.
- Semantic slide schema v2 is present in `src/data/models.py`.
- Storyline generation and QA orchestration are present in `src/core/storyline_engine.py`.
- Gemini model waterfall and key rotation exist in `src/core/model_cascade.py`.
- Layout normalization and fitting exist in `src/core/presentation_spec.py`.
- Editable PPTX rendering exists in `src/core/pptx_generator.py`.
- Primitive editable diagram helpers exist in `src/core/diagram_drawer.py`.
- Rendered-preview QA exists in `src/core/preview_qa.py`.
- Template support currently remains a static list in `src/data/templates.py`.

### Documentation

- Updated `ROADMAP.md` with commit baseline, code-verified status, AI Runtime plan, Presenton-inspired export/template priorities, and non-goals.
- Updated `ARCHITECTURE.md` with verified runtime flow, component responsibilities, architectural boundaries, and current risks.
- Updated `AGENT_RULES.md` with agent ownership, no-live-API unit test rules, secret-handling rules, and reference-repo adaptation rules.

### Verification

- Installed dependencies with `py -m pip install -r requirements.txt` during the initial audit.
- Ran `py -m pytest` during audit:
  - 40 passed.
  - 6 failed due to tests reaching live Gemini without a valid API key.
- Completed SG-001/SG-002 test isolation:
  - default `py -m pytest` now passes without real API keys or live provider calls;
  - latest result after SG-001/SG-002: 46 passed, 4 skipped;
  - live provider and manual OS-open checks are behind `integration` / `live_provider` markers;
  - image/illustrator/diagram tests write outputs to `tmp_path` instead of repo root or tracked asset folders.
- Completed SG-003 offline export layout coverage:
  - added `tests/test_export_layouts.py`;
  - added golden/offline PPTX layout export coverage for normal editable export, native chart/table/diagram scenarios, dense content warning/review banner behavior, and unsupported layout fallback warnings;
  - updated `src/core/pptx_generator.py` so unsupported layout variants fall back with explicit machine-checkable render warnings;
  - latest default `py -m pytest`: 50 passed, 4 skipped.
- Ran core import smoke check successfully.
- Ran PPTX export smoke script successfully:
  - `scripts/generate_workshop_psychological_safety.py` generated an 11-slide PPTX.

### Known issues

- Preview QA requires local Microsoft PowerPoint COM automation and should be treated as optional capability.
- Template support lacks a registry/capability matrix.
- Export/layout warnings need stronger offline regression coverage.
- `config.json` is still a tracked runtime config file and can be mutated by app/test startup paths.
