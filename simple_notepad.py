import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any

# Ensure src module resolution
src_dir = str(Path(__file__).parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import structlog

from t_e.config import settings
from t_e.services.file_service import FileService
from t_e.services.text_service import TextService

log = structlog.get_logger()


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SimpleNotepad(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        # ウィンドウの基本設定
        self.title(settings.app_title)
        icon_path = resource_path("file_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        self.geometry(settings.window_geometry)
        self.minsize(settings.min_window_width, settings.min_window_height)

        # カラーパレット（ダークモード）
        self.bg_main = "#1E1E1E"  # テキストエリア背景
        self.bg_top = "#2D2D30"  # トップバー背景
        self.bg_bottom = "#2D2D30"  # ステータスバー背景
        self.fg_main = "#CCCCCC"  # メインテキスト色
        self.fg_bottom = "#CCCCCC"  # ステータスバーテキスト色
        self.sel_bg = "#264F78"  # 選択範囲の背景色

        # フォント設定
        self.main_font = ("Yu Gothic UI", 12)
        self.ui_font = ("Yu Gothic UI", 10)

        # 状態変数
        self.current_file: str | None = None
        self.is_modified = False
        self.fr_window: tk.Toplevel | None = None
        self.encoding_var = tk.StringVar(value=settings.default_encoding)

        self.setup_ui()
        self.setup_bindings()
        self.update_title()
        self.update_char_count()
        self.set_dark_titlebar(self)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        if len(sys.argv) > 1:
            file_to_open = sys.argv[1]
            if os.path.isfile(file_to_open):
                self.after(50, lambda: self.load_file(file_to_open))

    def set_dark_titlebar(self, window: tk.Tk | tk.Toplevel) -> None:
        try:
            import ctypes

            window.update()
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value))

            bg = self.bg_top
            r = int(bg[1:3], 16)
            g = int(bg[3:5], 16)
            b = int(bg[5:7], 16)
            color = ctypes.c_int((b << 16) | (g << 8) | r)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(color), ctypes.sizeof(color))
        except Exception:  # noqa: BLE001, S110
            pass

    def setup_ui(self) -> None:
        self.top_frame = tk.Frame(self, bg=self.bg_top, height=45)
        self.top_frame.pack(side="top", fill="x")
        self.top_frame.pack_propagate(False)

        btn_config: dict[str, Any] = {
            "bg": self.bg_top,
            "fg": self.fg_main,
            "bd": 0,
            "font": self.ui_font,
            "activebackground": "#3E3E42",
            "activeforeground": "#FFFFFF",
            "cursor": "hand2",
        }

        buttons = [
            ("新規作成", self.new_file),
            ("開く", self.open_file),
            ("保存", self.save_file),
            ("名前を付けて保存", self.save_file_as),
            ("検索と置換", self.show_find_replace),
        ]

        for text, cmd in buttons:
            btn = tk.Button(self.top_frame, text=text, command=cmd, **btn_config)
            btn.pack(side="left", padx=5, pady=5, ipadx=10, ipady=2)
            self.add_hover(btn)

        self.text_area = tk.Text(
            self,
            bg=self.bg_main,
            fg=self.fg_main,
            insertbackground="#FFFFFF",
            selectbackground=self.sel_bg,
            font=self.main_font,
            undo=True,
            width=1,
            height=1,
            borderwidth=0,
            padx=15,
            pady=15,
        )
        self.text_area.pack(side="top", fill="both", expand=True)

        self.bottom_frame = tk.Frame(self, bg=self.bg_bottom, height=28)
        self.bottom_frame.pack(side="bottom", fill="x")
        self.bottom_frame.pack_propagate(False)

        self.char_count_label = tk.Label(
            self.bottom_frame, text="文字数: 0", bg=self.bg_bottom, fg=self.fg_bottom, font=self.ui_font
        )
        self.char_count_label.pack(side="left", padx=15)

        encodings = ["UTF-8", "Shift_JIS", "EUC-JP"]
        self.encoding_menu = tk.OptionMenu(self.bottom_frame, self.encoding_var, *encodings)
        self.encoding_menu.config(  # type: ignore[call-overload]
            bg=self.bg_bottom,
            fg=self.fg_bottom,
            activebackground=self.bg_bottom,
            activeforeground=self.fg_bottom,
            bd=0,
            highlightthickness=0,
            font=self.ui_font,
            indicatoron=0,
        )
        self.encoding_menu["menu"].config(
            bg="#2D2D30", fg="#FFFFFF", selectcolor="#007ACC", font=self.ui_font
        )
        self.encoding_menu.pack(side="right", padx=15, pady=2)

        self.encoding_label = tk.Label(
            self.bottom_frame,
            text="保存文字コード:",
            bg=self.bg_bottom,
            fg=self.fg_bottom,
            font=self.ui_font,
        )
        self.encoding_label.pack(side="right")

    def add_hover(self, btn: tk.Button) -> None:
        btn.bind("<Enter>", lambda e: btn.config(bg="#3E3E42"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.bg_top))

    def setup_bindings(self) -> None:
        self.text_area.bind("<KeyRelease>", self.update_char_count)
        self.text_area.bind("<<Modified>>", self.on_modify)

        self.bind("<Control-f>", self.show_find_replace)
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-n>", lambda e: self.new_file())

    def on_modify(self, event: tk.Event | None = None) -> None:
        if self.text_area.edit_modified():
            if not self.is_modified:
                self.is_modified = True
                self.update_title()
            self.update_char_count()
            self.text_area.edit_modified(False)

    def update_title(self) -> None:
        filename = os.path.basename(self.current_file) if self.current_file else "新規ファイル"
        mod_mark = "*" if self.is_modified else ""
        self.title(f"{settings.app_title} - {filename}{mod_mark}")

    def update_char_count(self, event: tk.Event | None = None) -> None:
        content = self.text_area.get("1.0", "end-1c")
        count = TextService.count_characters(content)
        self.char_count_label.config(text=f"文字数: {count}")

    def confirm_save_if_modified(self) -> bool:
        if not self.is_modified:
            return True

        file_name = os.path.basename(self.current_file) if self.current_file else "新規ファイル"
        response = messagebox.askyesnocancel(
            "保存の確認", f"「{file_name}」への変更内容を保存しますか？"
        )

        if response is True:
            return self.save_file()
        return response is False

    def on_closing(self) -> None:
        if self.confirm_save_if_modified():
            log.info("app_closing")
            self.destroy()

    def new_file(self) -> None:
        if not self.confirm_save_if_modified():
            return
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.is_modified = False
        self.text_area.edit_modified(False)
        self.encoding_var.set(settings.default_encoding)
        self.update_title()
        self.update_char_count()

    def open_file(self) -> None:
        if not self.confirm_save_if_modified():
            return
        filepath = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        self.load_file(filepath)

    def load_file(self, filepath: str) -> None:
        try:
            content, detected_enc = FileService.read_file(filepath)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.current_file = filepath
            self.is_modified = False
            self.text_area.edit_modified(False)
            self.encoding_var.set(detected_enc)
            self.update_title()
            self.update_char_count()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(
                "エラー", f"ファイルの読み込みに失敗しました:\n{e}"
            )

    def save_file(self) -> bool:
        if not self.current_file:
            return self.save_file_as()
        else:
            return self._write_to_disk(self.current_file)

    def save_file_as(self) -> bool:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            self.current_file = filepath
            return self._write_to_disk(filepath)
        return False

    def _write_to_disk(self, filepath: str) -> bool:
        content = self.text_area.get("1.0", "end-1c")
        enc = self.encoding_var.get()
        try:
            FileService.write_file(filepath, content, enc)
            self.is_modified = False
            self.text_area.edit_modified(False)
            self.update_title()
            return True
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("保存エラー", f"ファイルの保存に失敗しました:\n{e}")
            return False

    def show_find_replace(self, event: tk.Event | None = None) -> None:
        if self.fr_window is not None and self.fr_window.winfo_exists():
            self.fr_window.focus()
            return

        self.fr_window = tk.Toplevel(self)
        self.fr_window.title("検索と置換")
        self.fr_window.geometry("340x160")
        self.fr_window.configure(bg=self.bg_top)
        self.fr_window.resizable(False, False)
        self.fr_window.attributes("-topmost", True)
        self.set_dark_titlebar(self.fr_window)

        lbl_config: dict[str, Any] = {"bg": self.bg_top, "fg": self.fg_main, "font": self.ui_font}
        tk.Label(self.fr_window, text="検索:", **lbl_config).grid(
            row=0, column=0, padx=10, pady=15, sticky="e"
        )
        tk.Label(self.fr_window, text="置換:", **lbl_config).grid(
            row=1, column=0, padx=10, pady=5, sticky="e"
        )

        entry_config: dict[str, Any] = {
            "bg": self.bg_main,
            "fg": self.fg_main,
            "insertbackground": "#FFFFFF",
            "bd": 0,
            "font": self.ui_font,
        }
        find_entry = tk.Entry(self.fr_window, **entry_config)
        find_entry.grid(row=0, column=1, padx=5, pady=15, sticky="we", ipadx=5, ipady=3)
        replace_entry = tk.Entry(self.fr_window, **entry_config)
        replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we", ipadx=5, ipady=3)

        btn_frame = tk.Frame(self.fr_window, bg=self.bg_top)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)

        def find_next() -> None:
            query = find_entry.get()
            if not query:
                return

            self.text_area.tag_remove("sel", "1.0", tk.END)
            start_pos = self.text_area.index("insert")
            if self.text_area.tag_ranges("sel"):
                start_pos = self.text_area.index("sel.last")

            pos = self.text_area.search(query, start_pos, stopindex=tk.END)
            if not pos:
                pos = self.text_area.search(query, "1.0", stopindex=tk.END)

            if pos:
                end_pos = f"{pos}+{len(query)}c"
                self.text_area.tag_add("sel", pos, end_pos)
                self.text_area.mark_set("insert", end_pos)
                self.text_area.see(pos)
                self.text_area.focus()
            else:
                messagebox.showinfo("検索", "見つかりませんでした。", parent=self.fr_window)  # type: ignore[arg-type]

        def replace_current() -> None:
            if not self.text_area.tag_ranges("sel"):
                find_next()
                return

            query = find_entry.get()
            replacement = replace_entry.get()

            sel_start = self.text_area.index("sel.first")
            sel_end = self.text_area.index("sel.last")

            if self.text_area.get(sel_start, sel_end) == query:
                self.text_area.delete(sel_start, sel_end)
                self.text_area.insert(sel_start, replacement)
                find_next()

        def replace_all() -> None:
            query = find_entry.get()
            replacement = replace_entry.get()
            if not query:
                return

            content = self.text_area.get("1.0", "end-1c")
            new_content, count = TextService.replace_all(content, query, replacement)
            if count == 0:
                messagebox.showinfo("置換", "見つかりませんでした。", parent=self.fr_window)  # type: ignore[arg-type]
                return

            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", new_content)
            messagebox.showinfo("完了", f"{count} 箇所を置換しました。", parent=self.fr_window)  # type: ignore[arg-type]
            self.update_char_count()

        btn_conf: dict[str, Any] = {
            "bg": "#3E3E42",
            "fg": self.fg_main,
            "bd": 0,
            "font": self.ui_font,
            "activebackground": "#505050",
            "activeforeground": "#FFFFFF",
            "cursor": "hand2",
        }
        tk.Button(btn_frame, text="次を検索", command=find_next, **btn_conf).pack(
            side="left", padx=5, ipadx=5
        )
        tk.Button(btn_frame, text="置換", command=replace_current, **btn_conf).pack(
            side="left", padx=5, ipadx=5
        )
        tk.Button(btn_frame, text="すべて置換", command=replace_all, **btn_conf).pack(
            side="left", padx=5, ipadx=5
        )

        find_entry.focus()


if __name__ == "__main__":
    app = SimpleNotepad()
    app.mainloop()
