![CI](https://github.com/bottiLLC/T_E/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/Python-3.14-blue.svg) ![Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg) ![Mypy](https://img.shields.io/badge/Type%20Check-Mypy%20Strict-blue.svg) ![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg) ![License](https://img.shields.io/badge/License-Private-red.svg)

# T_E

## Overview
T_E is a lightweight, high-performance desktop text editor built with Python 3.14 and Tkinter, featuring automatic character encoding detection and native Windows dark mode integration. It provides deterministic filesystem I/O, robust unsaved buffer safety interlocks, and standardized data protection.

## Quick Start (TL;DR)
```bash
uv sync
uv run python main.py
uv run pytest -v -m "not fuzz" --cov=src --cov-branch --cov-report=term-missing
```

## Architecture & Features
- **Separation of Concerns Service Layer**: Core transformations isolated in stateless pure services (`FileService` for multi-encoding I/O and `TextService` for character/line metrics and replacements).
- **Multi-Encoding Auto-Detection**: Seamless bidirectional file reading and writing across UTF-8, Shift_JIS (CP932), and EUC-JP encodings.
- **Buffer Safety Interlocks**: Active buffer change tracking with visual indicators (`*`) and mandatory save confirmations upon window close or document switching.
- **Standardized Data Protection**: Project-root isolated `backup_manager.py` implementing atomic ZIP generation, `testzip()` integrity verification, and configurable target directories.
- **Cross-Platform Launcher Automation**: Zero-configuration bootstrapping via `run.bat` (Windows CRLF) and `run.command` (macOS/Linux LF) with automatic virtual environment provisioning.

## Environment Variables
| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `BACKUP_DIR` | `./backups` | Override path for integrity-verified backup archive output directory. |
| `APP_TITLE` | `T_E` | Custom display title prefix for application window. |
| `DEFAULT_ENCODING` | `UTF-8` | Default character encoding selected for new document buffers. |
| `LOG_LEVEL` | `INFO` | Structured logging verbosity level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

## Limits & Known Trade-offs
- **Single Tab Editing**: Currently constrained to single-document active editing per process window; multi-tab document buffering scheduled for future iteration.
- **Large File Streaming**: Files are currently ingested into memory in a single read pass; streaming chunks for files exceeding 100MB remains out-of-scope for the present architecture.
- **Rich Text / Syntax Highlighting**: Focused strictly on plaintext editing without AST token syntax coloring.

---

Copyright (c) LLC Bocchi. All rights reserved.
