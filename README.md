# T_E - Simple & Modern Text Editor

**T_E** は、Python 3.14 と Tkinter で構築された、高速かつモダンなダークモード対応テキストエディタです。  
関心事の分離 (Separation of Concerns) に基づく強固なサービスアーキテクチャ、多重文字コード自動判別、未保存変更の安全な保護機能を備えています。

---

## 🌟 主な特徴

- **モダンなダークモードデザイン**: Windows 10/11 のダークタイトルバーに連動した洗練されたUI。
- **安心の未保存保護機能**: 文書変更の自動追跡（タイトルバーの `*` マーク表記）および、終了・ファイル切り替え時の保存確認ダイアログ。
- **スマートな文字コード対応**: UTF-8 / Shift_JIS (cp932) / EUC-JP の自動読み込み判別と、指定文字コードでの保存機能。
- **テキスト操作サービス**: リアルタイム文字数カウント、前後ループ対応の文字列検索および一括置換機能。
- **ロバストな構造**: `structlog` による構造化ログ記録、および Pydantic V2 設定管理。
- **自動環境構築ランチャー**: `uv` パッケージマネージャーと連携し、ダブルクリック一発で `.venv` の作成・同期から起動までを自動化。

---

## 🛠️ 動作環境

- **Python**: 3.14 以上
- **パッケージマネージャー**: [uv](https://astral.sh/uv) (Astral)

---

## 🚀 クイックスタート

### ワンクリック起動（推奨）

- **Windows (黒い画面なし)**: [run.vbs](file:///e:/Python/T_E/run.vbs) をダブルクリック *(推奨)*
- **Windows (コンソール表示)**: [run.bat](file:///e:/Python/T_E/run.bat) をダブルクリック
- **Mac / Linux**: [run.command](file:///e:/Python/T_E/run.command) をダブルクリック  
  *(※初回のみターミナルで `chmod +x run.command` を実行してください)*

### コマンドラインからの起動

```bash
# 依存パッケージのインストールと同期
uv sync

# アプリケーションの起動
uv run python main.py
```

---

## 📁 プロジェクト構造

```text
T_E/
├── src/t_e/
│   ├── config.py           # Pydantic V2 & structlog 設定管理
│   └── services/
│       ├── file_service.py # 文字コード判別・ファイル入出力サービス
│       └── text_service.py # 文字数カウント・検索置換ロジック
├── tests/                  # ユニットテスト & Hypothesis ファジングテスト
├── simple_notepad.py       # GUI プレゼンテーション層 (Tkinter)
├── main.py                 # エントリーポイント
├── pyproject.toml          # シングルソース・オブ・トゥルース（プロジェクト定義）
├── run.bat                 # Windows用自動環境構築・起動スクリプト
└── run.command             # Mac/Linux用自動環境構築・起動スクリプト
```

---

## 🧪 開発およびテスト

本プロジェクトは、`ruff` (静的解析), `mypy` (厳格な型チェック), および `pytest` / `hypothesis` による継続的品質保証を行っています。

```bash
# 静的解析とコードフォーマット確認
uv run ruff check .

# 型チェック
uv run mypy .

# 自動テストおよびカバレッジ測定の実行
uv run pytest -v --cov=src
```
