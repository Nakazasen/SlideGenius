# Agent Rules for SlideGenius

These rules apply to coding agents working in this repository.

## Source of truth

1. Use the local repository as the source of truth:
   - `D:\Sandbox\SlideGenius`
2. Do not make roadmap or architecture conclusions from GitHub web pages alone.
3. After any merge, inspect the actual local code before updating documentation.
4. Keep reference repositories separate:
   - `D:\Sandbox\reference_repos\presenton`
   - `D:\Sandbox\reference_repos\translation_app`
5. Do not create duplicate roadmap/architecture/changelog/rules files under `docs/` unless explicitly requested.

## Agent ownership

### Codex

Codex owns high-risk and multi-file engineering work:

- code audit and technical review;
- AI Runtime design;
- provider/router logic;
- retry, cooldown, health, and attempt tracing;
- PowerPoint renderer and export pipeline;
- layout engine and validators;
- complex refactors;
- unit/integration tests;
- security and secrets handling.

### Gemini 3.1 Pro High

Gemini 3.1 Pro High owns product/design-heavy work:

- UI design and UX flows;
- product specs;
- prompt design;
- template style direction;
- simple product logic;
- orientation and planning documents.

### Gemini 3.5 Flash High

Gemini 3.5 Flash High owns lightweight Vietnamese-facing work:

- Vietnamese copy and microcopy;
- user-facing error/help text;
- Vietnamese prompts;
- simple test cases;
- light UI logic and guidance.

## Branching and merge discipline

1. Verify current branch and git status before edits.
2. Keep worktree clean except for intentional changes.
3. Do not overwrite user files or generated assets unless they are known smoke-test artifacts.
4. Record merge source, target, local branch, and commit hash in documentation when doing merge/audit work.
5. Do not claim remote `main` has been updated unless it has actually been pushed/verified.

## Testing rules

1. Prefer offline deterministic unit tests.
2. Do not let default unit tests call live Gemini or other provider APIs.
3. Mark live-provider checks as explicit integration tests.
4. Mark external provider/network checks with `live_provider` in addition to `integration`.
5. Keep default `py -m pytest` green without real API keys or network access.
6. Use fake clients/providers for provider routing, key rotation, fallback, cooldown, and error taxonomy.
7. Use `tmp_path` for generated test artifacts; do not write unit-test outputs into repo root or tracked asset folders.
8. For export work, run an offline PPTX smoke test when possible.
9. If tests fail because credentials are missing, document that as an integration-test configuration issue, not as product behavior.

## AI/provider rules

1. Keep provider routing separate from storyline and rendering logic.
2. Classify provider failures before deciding fallback behavior.
3. Track attempts with provider, model, key index/id, status, reason, latency, and retry-after.
4. Treat auth failures differently from quota, timeout, transport, token-limit, model-unavailable, and provider-5xx errors.
5. Never log raw API keys.
6. Do not copy `TranslationRequest`, `TranslationResult`, or translation-specific logic from `translation_app` into SlideGenius.
7. Generalize borrowed patterns into a presentation-generation AI Runtime contract.

## PPTX/export rules

1. Preserve editable PowerPoint output as the primary export goal.
2. Avoid flattening slides to images except for optional preview QA.
3. Add or update layout fixtures when changing renderer behavior.
4. Unknown layout variants should fail visibly or fall back with explicit warnings.
5. Dense content changes must update layout budgets and tests together.
6. Export warnings should be machine-checkable in tests, not only visible in logs.

## Preview QA rules

1. PowerPoint COM is optional and Windows/Office-dependent.
2. If preview rendering is unavailable, skip with a clear reason.
3. Preview QA findings must be stored as QA metadata, not hidden in logs only.
4. Auto-remediation must preserve intent and record what was changed.

## Documentation rules

1. Keep these root files current after major work:
   - `ROADMAP.md`
   - `ARCHITECTURE.md`
   - `AGENT_RULES.md`
   - `CHANGELOG.md`
2. README should describe user-facing stable behavior, not speculative features.
3. Roadmap claims must be traceable to code, tests, or explicit reference findings.
4. Use conservative language for unverified import/export fidelity.

## Reference-repo usage

1. Presenton is a reference for architecture boundaries, template/export services, provider config, document input, image/icon/chart services, background tasks, asset management, and observability.
2. translation_app is a reference for provider abstraction, model/key candidates, health state, cooldowns, error taxonomy, model ranking, attempt observability, config/secrets, and fake-provider tests.
3. Do not copy full architectures blindly; adapt only patterns that fit the desktop SlideGenius scope.
4. Do not rewrite SlideGenius into FastAPI/Next/Electron as a near-term phase.
