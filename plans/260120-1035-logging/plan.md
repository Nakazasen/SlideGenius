# Plan: Production Logging System

## Goal

Implement a robust, file-based logging system with rotation, formatting, and confidential data redaction.

## Features

- **Log Rotation:** Daily files, kept for 5 days.
- **Format:** `TIMESTAMP | LEVEL | MODULE | MESSAGE`
- **Location:** `logs/` directory in project root.
- **Privacy:** Mask API keys in logs.
- **UI:** "Open Logs Folder" button in Settings.

## Phases

### Phase 1: Core Logging Infrastructure

- [x] Create `src/utils/logger.py`:
  - [x] `setup_logging()` function.
  - [x] `TimedRotatingFileHandler` (Daily).
  - [x] Custom `Formatter` for `|` separator.
  - [x] Console handler for dev visibility.
- [x] Update `main.py` to initialize logging on startup.

### Phase 2: Integration

- [x] Update `src/core/model_cascade.py`: Use new logger.
- [x] Update `src/core/ai_service.py`: Log requests/responses.
- [x] Update `src/ui/dialogs/settings_dialog.py`: Trace user settings changes.

### Phase 3: UI Enhancements

- [x] Add "Open Logs Folder" button to `SettingsDialog`.

### Phase 4: Verification

- [x] Automated Verification: `scripts/verify_logging.py` confirmed log file creation (`logs/slidegenius.log`) and format.
