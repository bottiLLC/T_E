![CI](https://github.com/bottiLLC/T_E/actions/workflows/ci.yml/badge.svg) ![Python](https://img.shields.io/badge/Python-3.14-blue.svg) ![Ruff](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg) ![Mypy](https://img.shields.io/badge/Type%20Check-Mypy%20Strict-blue.svg) ![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg) ![License](https://img.shields.io/badge/License-Private-red.svg)

# T_E

## Overview
T_E は、Python 3.14 と Tkinter で構築された、多重文字コード自動判別および Windows ネイティブダークモード対応の高速デスクトップテキストエディタです。決定論的なファイル I/O、未保存バッファの保護インターロック、および標準化されたデータ整合性保護機能を提供します。

## Quick Start (TL;DR)
```bash
uv sync
uv run python main.py
uv run pytest -v -m "not fuzz" --cov=src --cov-branch --cov-report=term-missing
```

## Architecture & Features
- **関心事の分離に基づくサービス層**: コア変換処理をステートレスな純粋サービス（文字コード判別入出力 `FileService`、文字数・行数計算および文字列置換 `TextService`）として厳格に分離。
- **多重文字コード自動判別**: UTF-8、Shift_JIS（CP932）、EUC-JP 間の安全な双方向ファイル読み込みおよび書き込みに対応。
- **バッファ安全インターロック**: 未保存変更の自動追跡（タイトルバーの `*` 表記）および、ウィンドウ終了・新規作成時の保存確認ダイアログによるデータ損失防止。
- **標準データ保護モジュール**: プロジェクト直下の `backup_manager.py` によるアトミックな一時 ZIP 生成、`testzip()` 破損検証、および保存先設定の永続化。
- **自動起動スクリプト**: `run.bat`（Windows CRLF）および `run.command`（macOS/Linux LF）による、仮想環境自動プロビジョニング付きワンクリック起動。

## Environment Variables
| 環境変数名 | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `BACKUP_DIR` | `./backups` | 整合性検証付きバックアップ ZIP アーカイブの出力先ディレクトリ。 |
| `APP_TITLE` | `T_E` | アプリケーションウィンドウのタイトル表示プレフィックス。 |
| `DEFAULT_ENCODING` | `UTF-8` | 新規作成バッファに適用されるデフォルトの文字コード。 |
| `LOG_LEVEL` | `INFO` | structlog による構造化ログの出力レベル (`DEBUG`, `INFO`, `WARNING`, `ERROR`)。 |

## Limits & Known Trade-offs
- **単一ドキュメント編集の制約**: 現在は1プロセスあたり1ファイルの編集に制限されており、タブによる複数ドキュメント同時編集は次期マイレージでの対応予定。
- **大容量ファイルの一括メモリ読み込み**: 100MB を超える超巨大テキストのストリーミング分割読み込みは現行アーキテクチャのスコープ外。
- **シンタックスハイライト未対応**: プレーンテキストの高速・軽量な編集に特化しており、プログラミング言語の構文ハイライト機能は非搭載。

---

Copyright (c) LLC Bocchi. All rights reserved.
