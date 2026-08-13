# T_E - Simple & Modern Text Editor

**T_E** は、Python 3.12 と Tkinter で構築された、高速かつモダンなダークモード対応テキストエディタです。  
関心事の分離 (Separation of Concerns) に基づく強固なサービスアーキテクチャ、多重文字コード自動判別、未保存変更の安全な保護機能を備えています。

---

## 🌟 主な特徴

- **モダンなダークモードUI**: Windows 10/11 のダークタイトルバーに完全追従する洗練されたデザイン。
- **サイレント・ワンクリック起動**: `run.vbs` を使用し、黒いコンソール画面（ターミナル）を開かずにバックグラウンドで起動。
- **安心の未保存保護機能**: 文書変更の自動追跡（タイトルバーの `*` マーク表記）および、終了・ファイル切り替え時の保存確認ダイアログ。
- **スマートな文字コード＆改行コード対応**: UTF-8 / Shift_JIS (cp932) / EUC-JP の自動読み込み判別と、元の改行コードの正確な保持。
- **テキスト操作サービス**: リアルタイム文字数カウント、前後ループ対応の文字列検索および一括置換機能。
- **ロバストな構造と自動テスト**: `structlog` 構造化ログ、Pydantic V2 設定管理、Hypothesis ファジングテストを含む 92% の高テストカバレッジ。

---

## 🛠️ 動作環境

- **Python**: 3.12 以上 (※ Windows 11 の **Smart App Control (スマート アプリ コントロール)** 有効環境下では、未署名 DLL ブロック回避のため、Tcl/Tk DLL が公式にデジタル署名された **Python 3.12 または 3.13 の安定版公式インストーラー経由のインストール** を強く推奨します)
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
# 依存パッケージのインストールと環境同期
uv sync

# アプリケーションの起動
uv run python main.py
```

### 📦 スタンドアロン実行ファイルのビルド (1フォルダ形式 / exe化)

Pythonがインストールされていない環境向けに、単一フォルダ形式の配布用 `exe` をビルドできます。

```bash
# PyInstallerによる1フォルダ形式(onedir)ビルド
uv run pyinstaller --noconfirm T_E.spec
```

ビルド成功後、`dist/T_E/` フォルダ内に `T_E.exe` および必要な依存ファイル群が生成されます。

---

## 📁 プロジェクト構造

```text
T_E/
├── .github/workflows/ci.yml  # GitHub Actions CI/CD パイプライン
├── src/t_e/
│   ├── config.py             # Pydantic V2 & structlog 設定管理
│   └── services/
│       ├── file_service.py   # 文字コード判別・ファイル入出力サービス
│       └── text_service.py   # 文字数カウント・検索置換ロジック
├── tests/                    # ユニットテスト & Hypothesis ファジングテスト
├── simple_notepad.py         # GUI プレゼンテーション層 (Tkinter)
├── T_E.spec                  # PyInstaller ビルド定義仕様
├── main.py                   # アプリケーションエントリーポイント
├── LICENSE                   # GNU General Public License v3.0 (GPL-3.0)
├── pyproject.toml            # プロジェクト定義（Single Source of Truth）
├── run.vbs                   # Windows用サイレント起動スクリプト (画面なし)
├── run.bat                   # Windows用環境構築・起動スクリプト
└── run.command               # Mac/Linux用環境構築・起動スクリプト
```

---

## 🧪 開発およびテスト品質保証

本プロジェクトは、`ruff` (静的解析), `mypy` (厳格な型チェック), および `pytest` / `hypothesis` (ファジング) による継続的品質保証を行っています。

```bash
# 静的解析とコードフォーマット確認
uv run ruff check .

# 厳格な型チェック
uv run mypy .

# 自動テストおよびカバレッジ測定の実行 (現在 92% Coverage)
uv run pytest -v --cov=src
```

---

## 📄 ライセンス

本プロジェクトは [GNU General Public License v3.0 (GPL-3.0)](file:///e:/Python/T_E/LICENSE) のもとで公開されています。詳細については [LICENSE](file:///e:/Python/T_E/LICENSE) ファイルをご参照ください。
