import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SimpleNotepad(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # ウィンドウの基本設定
        self.title("T_E")
        icon_path = resource_path("file_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        self.geometry("900x600")
        self.minsize(400, 300)
        
        # カラーパレット（ダークモード）
        self.bg_main = "#1E1E1E"    # テキストエリア背景
        self.bg_top = "#2D2D30"     # トップバー背景
        self.bg_bottom = "#2D2D30"  # ステータスバー背景
        self.fg_main = "#CCCCCC"    # メインテキスト色
        self.fg_bottom = "#CCCCCC"  # ステータスバーテキスト色
        self.sel_bg = "#264F78"     # 選択範囲の背景色
        
        # フォント設定
        self.main_font = ("Yu Gothic UI", 12)
        self.ui_font = ("Yu Gothic UI", 10)
        
        # 状態変数
        self.current_file = None
        self.encoding_var = tk.StringVar(value="UTF-8")
        
        self.setup_ui()
        self.setup_bindings()
        self.update_char_count()
        self.set_dark_titlebar(self)
        
        if len(sys.argv) > 1:
            file_to_open = sys.argv[1]
            if os.path.isfile(file_to_open):
                self.after(50, lambda: self.load_file(file_to_open))
        
    def set_dark_titlebar(self, window):
        try:
            import ctypes
            window.update()
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            # Windows 10: Enable Dark Mode
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(value), ctypes.sizeof(value))
            
            # Windows 11: Set exact color to match top bar
            bg = self.bg_top
            r = int(bg[1:3], 16)
            g = int(bg[3:5], 16)
            b = int(bg[5:7], 16)
            color = ctypes.c_int((b << 16) | (g << 8) | r)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(color), ctypes.sizeof(color))
        except Exception:
            pass

    def setup_ui(self):
        # 1. トップバー（メニューの代わりになるフラットなボタン群）
        self.top_frame = tk.Frame(self, bg=self.bg_top, height=45)
        self.top_frame.pack(side="top", fill="x")
        self.top_frame.pack_propagate(False)
        
        btn_config = {
            "bg": self.bg_top, "fg": self.fg_main, "bd": 0, "font": self.ui_font,
            "activebackground": "#3E3E42", "activeforeground": "#FFFFFF", "cursor": "hand2"
        }
        
        # ボタンの配置
        buttons = [
            ("新規作成", self.new_file),
            ("開く", self.open_file),
            ("保存", self.save_file),
            ("名前を付けて保存", self.save_file_as),
            ("検索と置換", self.show_find_replace)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(self.top_frame, text=text, command=cmd, **btn_config)
            btn.pack(side="left", padx=5, pady=5, ipadx=10, ipady=2)
            self.add_hover(btn)
        
        # 2. テキストエリア（大きめ12ptのフォント）
        self.text_area = tk.Text(self, bg=self.bg_main, fg=self.fg_main, insertbackground="#FFFFFF",
                                 selectbackground=self.sel_bg, font=self.main_font,
                                 undo=True, width=1, height=1, borderwidth=0, padx=15, pady=15)
        self.text_area.pack(side="top", fill="both", expand=True)

        # 3. ボトムステータスバー
        self.bottom_frame = tk.Frame(self, bg=self.bg_bottom, height=28)
        self.bottom_frame.pack(side="bottom", fill="x")
        self.bottom_frame.pack_propagate(False)
        
        # 文字数カウント表示箇所
        self.char_count_label = tk.Label(self.bottom_frame, text="文字数: 0", bg=self.bg_bottom, fg=self.fg_bottom, font=self.ui_font)
        self.char_count_label.pack(side="left", padx=15)
        
        # 文字コード選択UI
        encodings = ["UTF-8", "Shift_JIS", "EUC-JP"]
        self.encoding_menu = tk.OptionMenu(self.bottom_frame, self.encoding_var, *encodings)
        self.encoding_menu.config(bg=self.bg_bottom, fg=self.fg_bottom, activebackground=self.bg_bottom, 
                                  activeforeground=self.fg_bottom, bd=0, highlightthickness=0, font=self.ui_font, indicatoron=0)
        self.encoding_menu["menu"].config(bg="#2D2D30", fg="#FFFFFF", selectcolor="#007ACC", font=self.ui_font)
        self.encoding_menu.pack(side="right", padx=15, pady=2)
        
        self.encoding_label = tk.Label(self.bottom_frame, text="保存文字コード:", bg=self.bg_bottom, fg=self.fg_bottom, font=self.ui_font)
        self.encoding_label.pack(side="right")
        
    def add_hover(self, btn):
        btn.bind("<Enter>", lambda e: btn.config(bg="#3E3E42"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.bg_top))
        
    def setup_bindings(self):
        # リアルタイム文字数カウント用
        self.text_area.bind("<KeyRelease>", self.update_char_count)
        self.text_area.bind("<<Modified>>", self.on_modify)
        
        # ショートカットキー対応（Ctrl+C, Ctrl+Vは標準で動作します）
        self.bind("<Control-f>", self.show_find_replace)
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-n>", lambda e: self.new_file())

    def on_modify(self, event=None):
        self.update_char_count()
        # Modifiedフラグをリセットしないと次のイベントが発火しない
        self.text_area.edit_modified(False)

    def update_char_count(self, event=None):
        # 1.0からend-1cまでを取得し、正確な文字数をカウント
        content = self.text_area.get("1.0", "end-1c")
        self.char_count_label.config(text=f"文字数: {len(content)}")
        
    def new_file(self):
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.encoding_var.set("UTF-8")
        self.title("T_E - 新規ファイル")
        self.update_char_count()
        
    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath:
            return
            
        self.load_file(filepath)
        
    def load_file(self, filepath):
        # 複数エンコーディングの読み込みフォールバック
        encodings_to_try = ["utf-8", "cp932", "euc-jp"] # cp932はWindowsのShift_JIS
        content = None
        used_enc = None
        
        for enc in encodings_to_try:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    content = f.read()
                used_enc = enc
                break
            except UnicodeDecodeError:
                continue
                
        if content is None:
            messagebox.showerror("エラー", "ファイルの読み込みに失敗しました。\n対応していない文字コードです。")
            return
            
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)
        self.current_file = filepath
        
        # 読み込めたエンコーディングをUIに反映
        if used_enc == "utf-8":
            self.encoding_var.set("UTF-8")
        elif used_enc == "cp932":
            self.encoding_var.set("Shift_JIS")
        elif used_enc == "euc-jp":
            self.encoding_var.set("EUC-JP")
            
        self.title(f"T_E - {os.path.basename(filepath)}")
        self.update_char_count()
        
    def save_file(self):
        if not self.current_file:
            self.save_file_as()
        else:
            self._write_to_disk(self.current_file)
            
    def save_file_as(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            self.current_file = filepath
            self._write_to_disk(filepath)
            
    def _write_to_disk(self, filepath):
        content = self.text_area.get("1.0", "end-1c")
        enc = self.encoding_var.get()
        
        # UI表記からPythonのエンコーディング名へマッピング
        enc_map = {"UTF-8": "utf-8", "Shift_JIS": "cp932", "EUC-JP": "euc-jp"}
        target_enc = enc_map.get(enc, "utf-8")
        
        try:
            with open(filepath, "w", encoding=target_enc) as f:
                f.write(content)
            self.title(f"T_E - {os.path.basename(filepath)}")
            # 保存完了のポップアップはシンプルさを損なうためステータスバーを更新するか省略します
        except Exception as e:
            messagebox.showerror("保存エラー", f"ファイルの保存に失敗しました:\n{e}")
            
    def show_find_replace(self, event=None):
        # 既に開いている場合はフォーカス
        if hasattr(self, 'fr_window') and self.fr_window.winfo_exists():
            self.fr_window.focus()
            return
            
        self.fr_window = tk.Toplevel(self)
        self.fr_window.title("検索と置換")
        self.fr_window.geometry("340x160")
        self.fr_window.configure(bg=self.bg_top)
        self.fr_window.resizable(False, False)
        # 前面に維持する
        self.fr_window.attributes("-topmost", True)
        self.set_dark_titlebar(self.fr_window)
        
        lbl_config = {"bg": self.bg_top, "fg": self.fg_main, "font": self.ui_font}
        tk.Label(self.fr_window, text="検索:", **lbl_config).grid(row=0, column=0, padx=10, pady=15, sticky="e")
        tk.Label(self.fr_window, text="置換:", **lbl_config).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        
        entry_config = {"bg": self.bg_main, "fg": self.fg_main, "insertbackground": "#FFFFFF", "bd": 0, "font": self.ui_font}
        find_entry = tk.Entry(self.fr_window, **entry_config)
        find_entry.grid(row=0, column=1, padx=5, pady=15, sticky="we", ipadx=5, ipady=3)
        replace_entry = tk.Entry(self.fr_window, **entry_config)
        replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we", ipadx=5, ipady=3)
        
        btn_frame = tk.Frame(self.fr_window, bg=self.bg_top)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        def find_next():
            query = find_entry.get()
            if not query: return
            
            # 以前のハイライトを削除
            self.text_area.tag_remove("sel", "1.0", tk.END)
            
            start_pos = self.text_area.index("insert")
            if self.text_area.tag_ranges("sel"):
                start_pos = self.text_area.index("sel.last")
                
            pos = self.text_area.search(query, start_pos, stopindex=tk.END)
            if not pos:
                # ページ最後まで検索後、最初から再度検索
                pos = self.text_area.search(query, "1.0", stopindex=tk.END)
                
            if pos:
                end_pos = f"{pos}+{len(query)}c"
                self.text_area.tag_add("sel", pos, end_pos)
                self.text_area.mark_set("insert", end_pos)
                self.text_area.see(pos)
                self.text_area.focus()
            else:
                messagebox.showinfo("検索", "見つかりませんでした。", parent=self.fr_window)
                
        def replace_current():
            # 選択範囲がない場合は次を検索
            if not self.text_area.tag_ranges("sel"):
                find_next()
                return
            
            query = find_entry.get()
            replacement = replace_entry.get()
            
            sel_start = self.text_area.index("sel.first")
            sel_end = self.text_area.index("sel.last")
            
            # 選択中のテキストが検索文字列と一致するか確認
            if self.text_area.get(sel_start, sel_end) == query:
                self.text_area.delete(sel_start, sel_end)
                self.text_area.insert(sel_start, replacement)
                find_next()
                
        def replace_all():
            query = find_entry.get()
            replacement = replace_entry.get()
            if not query: return
            
            content = self.text_area.get("1.0", "end-1c")
            count = content.count(query)
            if count == 0:
                messagebox.showinfo("置換", "見つかりませんでした。", parent=self.fr_window)
                return
                
            new_content = content.replace(query, replacement)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", new_content)
            
            messagebox.showinfo("完了", f"{count} 箇所を置換しました。", parent=self.fr_window)
            self.update_char_count()
            
        btn_conf = {"bg": "#3E3E42", "fg": self.fg_main, "bd": 0, "font": self.ui_font, "activebackground": "#505050", "activeforeground": "#FFFFFF", "cursor": "hand2"}
        tk.Button(btn_frame, text="次を検索", command=find_next, **btn_conf).pack(side="left", padx=5, ipadx=5)
        tk.Button(btn_frame, text="置換", command=replace_current, **btn_conf).pack(side="left", padx=5, ipadx=5)
        tk.Button(btn_frame, text="すべて置換", command=replace_all, **btn_conf).pack(side="left", padx=5, ipadx=5)
        
        find_entry.focus()
        
if __name__ == "__main__":
    app = SimpleNotepad()
    app.mainloop()
