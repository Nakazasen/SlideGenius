# Plan: API Key Rotation

## Goal

Implement support for multiple Gemini API keys with automatic rotation to handle rate limits (429) and quota exhaustion.

## Phases

### Phase 1: Core & Data

- [x] Update `ConfigManager` to support `api.gemini_keys` (list) and migrate legacy `api.gemini_key`.
- [x] Update `ModelCascade` to load multiple keys.
- [x] Implement `Round-Robin` or `Random` rotation strategy in `ModelCascade`.
- [x] Implement `Retry-on-429` logic: If a key fails with quota error, switch key and retry.

### Phase 2: UI

- [x] Update `SettingsDialog`:
  - [x] Replace `QLineEdit` (password) with `QPlainTextEdit` (multi-line).
  - [x] Logic to parse newline-separated keys.
  - [x] Update "Test Connection" to check validity of keys.

### Phase 3: Verification

- [x] Manual test: Input multiple keys, verify they are saved.
- [x] Manual test: "Test Connection" works with multiple keys.
- [x] Automated test: `tests/test_key_rotation.py` PASSED.
