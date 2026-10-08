# Silent Launcher Rule

## Window Launch Behavior Invariant
- `run.bat` から本アプリケーションを起動する際、コマンドプロンプトやターミナルのコンソールウィンドウは一切開かず、アプリケーションの GUI ウィンドウ（Tkinter）のみを表示すること。
- `run.bat` は起動時にサイレント実行フラグ（`--silent`）を検知し、通常起動（引数なし）時は `run.vbs`（WScript.Shell による非表示起動、Window Style 0）または PowerShell バックグラウンドプロセスへ自動的に委譲して自身を直ちに終了すること。
- アプリケーション終了時にバックグラウンドで `cmd.exe` が残留しないよう、サイレント起動モードでは不要な `pause` コマンドを実行しないこと。
- GUI 起動時はコンソールを持たない `pythonw` または完全非表示化された Python プロセスとして実行すること。
